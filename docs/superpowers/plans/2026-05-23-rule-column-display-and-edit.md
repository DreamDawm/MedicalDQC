# 校验规则页面优化实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 优化校验规则页面的列名显示格式，并添加编辑功能

**Architecture:**
- 后端：修改列信息获取服务，通过 INFORMATION_SCHEMA 查询获取列注释，过滤掉 collate 等无关信息
- 前端：更新列名显示格式为 `英文字段 (类型) 中文注释`，添加编辑按钮和编辑对话框

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, Element Plus

---

## 文件结构

| 文件 | 职责 |
|-----|------|
| `backend/app/schemas/datasource.py` | 添加 `comment` 字段到 ColumnInfo |
| `backend/app/services/datasource_service.py` | 修改 get_columns 函数，通过 INFORMATION_SCHEMA 获取列注释 |
| `frontend/src/views/RuleConfigView.vue` | 更新列名显示格式，添加编辑按钮和编辑对话框 |

---

### Task 1: 扩展 ColumnInfo Schema 添加注释字段

**Files:**
- Modify: `backend/app/schemas/datasource.py:44-48`

- [ ] **Step 1: 修改 ColumnInfo 类添加 comment 字段**

```python
class ColumnInfo(BaseModel):
    column_name: str
    data_type: str
    is_nullable: bool
    comment: str = ""  # 列注释，默认空字符串
```

- [ ] **Step 2: 验证 Schema 定义正确**

运行: `cd D:/python_pro/dataqc/backend && python -c "from app.schemas.datasource import ColumnInfo; print(ColumnInfo.model_fields)"`
预期: 输出包含 `comment` 字段

- [ ] **Step 3: 提交**

```bash
git add backend/app/schemas/datasource.py
git commit -m "feat(schema): ColumnInfo 添加 comment 字段"
```

---

### Task 2: 修改后端服务获取列注释

**Files:**
- Modify: `backend/app/services/datasource_service.py:35-46`

- [ ] **Step 1: 修改 get_columns 函数**

```python
def get_columns(url: str, table_name: str) -> list[dict]:
    engine = create_engine(url)
    inspector = inspect(engine)

    # 从 URL 中提取数据库名和数据库类型
    # URL 格式: mysql+pymysql://user:pass@host:port/database
    db_type = "mysql" if "mysql" in url else "postgresql" if "postgresql" in url else "sqlserver"
    database = url.split("/")[-1].split("?")[0]

    # 获取基础列信息
    columns = inspector.get_columns(table_name)

    # 对于 MySQL，查询 INFORMATION_SCHEMA 获取列注释
    comment_map = {}
    if db_type == "mysql":
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT COLUMN_NAME, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{database}' AND TABLE_NAME = '{table_name}'
            """))
            for row in result:
                comment_map[row[0]] = row[1] or ""

    return [
        {
            "column_name": col["name"],
            # 只保留类型名称，移除 collate 等额外信息
            "data_type": str(col["type"]).split("(")[0].upper(),
            "is_nullable": col.get("nullable", True),
            "comment": comment_map.get(col["name"], ""),
        }
        for col in columns
    ]
```

- [ ] **Step 2: 测试列信息获取**

运行: `cd D:/python_pro/dataqc && python -c "
from app.services.datasource_service import get_columns
url = 'mysql+pymysql://root:123456@localhost:3306/vinci_difficult'
cols = get_columns(url, 'visit_occurrence')
for c in cols[:3]:
    print(f\"{c['column_name']} | {c['data_type']} | '{c['comment']}'\")
"`
预期: 输出列名、类型（不含 collate）、注释

- [ ] **Step 3: 提交**

```bash
git add backend/app/services/datasource_service.py
git commit -m "feat(service): 获取列注释并简化类型显示"
```

---

### Task 3: 前端更新列名显示格式

**Files:**
- Modify: `frontend/src/views/RuleConfigView.vue:50-53`

- [ ] **Step 1: 修改列名选择器的显示格式**

找到第 50-53 行的 el-select，修改 label 格式：

```vue
<el-form-item label="列名">
  <el-select v-model="form.column_name" clearable style="width: 100%">
    <el-option
      v-for="c in columns"
      :key="c.column_name"
      :label="formatColumnLabel(c)"
      :value="c.column_name"
    />
  </el-select>
</el-form-item>
```

- [ ] **Step 2: 添加 formatColumnLabel 函数**

在 `<script setup>` 部分添加函数（约第 111 行后）：

```javascript
function formatColumnLabel(col) {
  // 格式：英文字段 (类型) 中文注释
  const parts = [col.column_name, `(${col.data_type})`]
  if (col.comment) {
    parts.push(col.comment)
  }
  return parts.join(' ')
}
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/RuleConfigView.vue
git commit -m "feat(frontend): 列名显示格式优化为 字段名(类型)中文注释"
```

---

### Task 4: 前端添加编辑功能

**Files:**
- Modify: `frontend/src/views/RuleConfigView.vue`

- [ ] **Step 1: 添加编辑状态变量和编辑对话框**

在 `const showDialog = ref(false)` 后（约第 91 行）添加：

```javascript
const editDialog = ref(false)
const editingRule = ref(null)
```

- [ ] **Step 2: 修改操作列添加编辑按钮**

修改第 30-34 行：

```vue
<el-table-column label="操作" width="180">
  <template #default="{ row }">
    <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
    <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
  </template>
</el-table-column>
```

- [ ] **Step 3: 添加编辑对话框**

在新建对话框（`</el-dialog>`）后添加编辑对话框：

```vue
<!-- 编辑规则对话框 -->
<el-dialog v-model="editDialog" title="编辑校验规则" width="600px">
  <el-form :model="editForm" label-width="100px">
    <el-form-item label="数据源">
      <el-select v-model="editForm.datasource_id" @change="onEditDatasourceChange" style="width: 100%">
        <el-option v-for="ds in datasources" :key="ds.id" :label="ds.name" :value="ds.id" />
      </el-select>
    </el-form-item>
    <el-form-item label="表名">
      <el-select v-model="editForm.table_name" @change="onEditTableChange" style="width: 100%">
        <el-option v-for="t in editTables" :key="t.table_name" :label="t.table_name" :value="t.table_name" />
      </el-select>
    </el-form-item>
    <el-form-item label="列名">
      <el-select v-model="editForm.column_name" clearable style="width: 100%">
        <el-option
          v-for="c in editColumns"
          :key="c.column_name"
          :label="formatColumnLabel(c)"
          :value="c.column_name"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="校验规则">
      <RuleSelector v-model="editForm.builtin_rule_id" :rules="builtinRules" @change="onEditRuleChange" />
    </el-form-item>
    <el-form-item label="容忍度">
      <el-input-number v-model="editForm.mostly" :min="0" :max="1" :step="0.05" :precision="2" />
    </el-form-item>
    <el-form-item label="严重等级">
      <el-select v-model="editForm.severity" style="width: 100%">
        <el-option label="critical" value="critical" />
        <el-option label="warning" value="warning" />
        <el-option label="info" value="info" />
      </el-select>
    </el-form-item>
    <ParameterForm v-if="editSelectedRule" :schema="editSelectedRule.parameters_schema" v-model="editForm.parameters" />
  </el-form>
  <template #footer>
    <el-button @click="editDialog = false">取消</el-button>
    <el-button type="primary" @click="handleUpdate" :loading="saving">保存</el-button>
  </template>
</el-dialog>
```

- [ ] **Step 4: 添加编辑相关变量和计算属性**

在 `const columns = ref([])` 后添加：

```javascript
const editTables = ref([])
const editColumns = ref([])
```

在 `const selectedRule = computed(...)` 后添加：

```javascript
const editSelectedRule = computed(() =>
  builtinRules.value.find(r => r.id === editForm.value.builtin_rule_id)
)
```

- [ ] **Step 5: 添加编辑表单数据**

在 `const form = ref({...})` 后添加：

```javascript
const editForm = ref({
  id: '',
  datasource_id: '',
  table_name: '',
  column_name: '',
  builtin_rule_id: '',
  parameters: {},
  mostly: null,
  severity: 'warning',
  enabled: true,
})
```

- [ ] **Step 6: 添加编辑相关函数**

在 `handleDelete` 函数前添加：

```javascript
async function handleEdit(rule) {
  // 查找规则对应的数据源
  const ds = datasources.value.find(d => d.name === rule.datasource_name || d.id === rule.datasource_id)
  if (!ds) {
    ElMessage.warning('未找到对应的数据源')
    return
  }

  editForm.value = {
    id: rule.id,
    datasource_id: ds.id,
    table_name: rule.table_name,
    column_name: rule.column_name,
    builtin_rule_id: rule.builtin_rule_id,
    parameters: rule.parameters || {},
    mostly: rule.mostly,
    severity: rule.severity,
    enabled: rule.enabled,
  }

  // 加载表和列
  try {
    const { data: tableData } = await datasourceApi.getTables(ds.id)
    editTables.value = tableData

    if (rule.table_name) {
      const { data: colData } = await datasourceApi.getColumns(ds.id, rule.table_name)
      editColumns.value = colData
    }
  } catch {
    ElMessage.error('加载数据失败')
  }

  editDialog.value = true
}

async function onEditDatasourceChange(dsId) {
  editTables.value = []
  editColumns.value = []
  editForm.value.table_name = ''
  editForm.value.column_name = ''
  if (dsId) {
    const { data } = await datasourceApi.getTables(dsId)
    editTables.value = data
  }
}

async function onEditTableChange(table) {
  editColumns.value = []
  editForm.value.column_name = ''
  if (table && editForm.value.datasource_id) {
    const { data } = await datasourceApi.getColumns(editForm.value.datasource_id, table)
    editColumns.value = data
  }
}

function onEditRuleChange() {
  editForm.value.parameters = {}
}

async function handleUpdate() {
  saving.value = true
  try {
    await validationRuleApi.update(editForm.value.id, editForm.value)
    ElMessage.success('规则更新成功')
    editDialog.value = false
    loadData()
  } catch {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}
```

- [ ] **Step 7: 验证编辑功能**

启动前端开发服务器，测试：
1. 规则列表每行显示编辑按钮
2. 点击编辑打开对话框，数据正确回填
3. 修改后保存，列表更新

- [ ] **Step 8: 提交**

```bash
git add frontend/src/views/RuleConfigView.vue
git commit -m "feat(frontend): 添加校验规则编辑功能"
```

---

## 验收标准

- [ ] 列名显示格式为 `英文字段 (类型) 中文注释`，无 collate 等额外信息
- [ ] 规则列表每行有编辑按钮
- [ ] 编辑对话框正确回填现有数据
- [ ] 编辑后保存成功，列表刷新显示更新后的数据
