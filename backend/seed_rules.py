from app.database import SessionLocal, engine, Base
from app.models.builtin_rule import BuiltinRule

RULES = [
    # 一、完整性校验
    {
        "expectation_type": "expect_column_values_to_not_be_null",
        "display_name": "非空检查",
        "category": "完整性校验",
        "description": "检查列值是否为非空",
        "parameters_schema": {},
    },
    {
        "expectation_type": "expect_column_values_to_be_null",
        "display_name": "空值检查",
        "category": "完整性校验",
        "description": "检查列值是否全部为空",
        "parameters_schema": {},
    },
    {
        "expectation_type": "expect_table_row_count_to_equal",
        "display_name": "行数精确匹配",
        "category": "完整性校验",
        "description": "检查表行数是否等于指定值",
        "parameters_schema": {"value": {"type": "integer", "label": "期望行数"}},
    },
    {
        "expectation_type": "expect_table_row_count_to_be_between",
        "display_name": "行数范围检查",
        "category": "完整性校验",
        "description": "检查表行数是否在指定范围内",
        "parameters_schema": {
            "min_value": {"type": "integer", "label": "最小行数"},
            "max_value": {"type": "integer", "label": "最大行数"},
        },
    },
    {
        "expectation_type": "expect_column_proportion_of_unique_values_to_be_between",
        "display_name": "唯一值比例检查",
        "category": "完整性校验",
        "description": "检查列唯一值比例是否在指定范围内",
        "parameters_schema": {
            "min_value": {"type": "float", "label": "最小比例"},
            "max_value": {"type": "float", "label": "最大比例"},
        },
    },
    # 二、唯一性与主键校验
    {
        "expectation_type": "expect_column_values_to_be_unique",
        "display_name": "唯一性检查",
        "category": "唯一性与主键校验",
        "description": "检查列值是否唯一",
        "parameters_schema": {},
    },
    {
        "expectation_type": "expect_compound_columns_to_be_unique",
        "display_name": "复合唯一性检查",
        "category": "唯一性与主键校验",
        "description": "检查多列组合是否唯一",
        "parameters_schema": {"column_list": {"type": "array", "label": "列名列表"}},
    },
    {
        "expectation_type": "expect_select_column_values_to_be_unique_within_record",
        "display_name": "记录内列唯一性",
        "category": "唯一性与主键校验",
        "description": "检查同一行内指定列的值是否唯一",
        "parameters_schema": {"column_list": {"type": "array", "label": "列名列表"}},
    },
    # 三、数据类型与格式校验
    {
        "expectation_type": "expect_column_values_to_be_of_type",
        "display_name": "数据类型检查",
        "category": "数据类型与格式校验",
        "description": "检查列值是否为指定数据类型",
        "parameters_schema": {"type_": {"type": "string", "label": "期望类型"}},
    },
    {
        "expectation_type": "expect_column_values_to_match_regex",
        "display_name": "正则匹配",
        "category": "数据类型与格式校验",
        "description": "检查列值是否匹配正则表达式",
        "parameters_schema": {"regex": {"type": "string", "label": "正则表达式"}},
    },
    {
        "expectation_type": "expect_column_values_to_match_strftime_format",
        "display_name": "日期格式检查",
        "category": "数据类型与格式校验",
        "description": "检查列值是否匹配日期格式",
        "parameters_schema": {"strftime_format": {"type": "string", "label": "日期格式"}},
    },
    {
        "expectation_type": "expect_column_value_lengths_to_be_between",
        "display_name": "字符串长度范围",
        "category": "数据类型与格式校验",
        "description": "检查列值字符串长度是否在范围内",
        "parameters_schema": {
            "min_value": {"type": "integer", "label": "最小长度"},
            "max_value": {"type": "integer", "label": "最大长度"},
        },
    },
    {
        "expectation_type": "expect_column_values_to_not_match_regex",
        "display_name": "正则排除",
        "category": "数据类型与格式校验",
        "description": "检查列值是否不匹配正则表达式",
        "parameters_schema": {"regex": {"type": "string", "label": "正则表达式"}},
    },
    # 四、数据范围与数值校验
    {
        "expectation_type": "expect_column_values_to_be_between",
        "display_name": "值范围检查",
        "category": "数据范围与数值校验",
        "description": "检查列值是否在指定范围内",
        "parameters_schema": {
            "min_value": {"type": "number", "label": "最小值"},
            "max_value": {"type": "number", "label": "最大值"},
        },
    },
    {
        "expectation_type": "expect_column_max_to_be_between",
        "display_name": "最大值范围检查",
        "category": "数据范围与数值校验",
        "description": "检查列最大值是否在指定范围内",
        "parameters_schema": {
            "min_value": {"type": "number", "label": "最小值"},
            "max_value": {"type": "number", "label": "最大值"},
        },
    },
    {
        "expectation_type": "expect_column_min_to_be_between",
        "display_name": "最小值范围检查",
        "category": "数据范围与数值校验",
        "description": "检查列最小值是否在指定范围内",
        "parameters_schema": {
            "min_value": {"type": "number", "label": "最小值"},
            "max_value": {"type": "number", "label": "最大值"},
        },
    },
    {
        "expectation_type": "expect_column_mean_to_be_between",
        "display_name": "均值范围检查",
        "category": "数据范围与数值校验",
        "description": "检查列均值是否在指定范围内",
        "parameters_schema": {
            "min_value": {"type": "number", "label": "最小值"},
            "max_value": {"type": "number", "label": "最大值"},
        },
    },
    {
        "expectation_type": "expect_column_median_to_be_between",
        "display_name": "中位数范围检查",
        "category": "数据范围与数值校验",
        "description": "检查列中位数是否在指定范围内",
        "parameters_schema": {
            "min_value": {"type": "number", "label": "最小值"},
            "max_value": {"type": "number", "label": "最大值"},
        },
    },
    {
        "expectation_type": "expect_column_stdev_to_be_between",
        "display_name": "标准差范围检查",
        "category": "数据范围与数值校验",
        "description": "检查列标准差是否在指定范围内",
        "parameters_schema": {
            "min_value": {"type": "number", "label": "最小值"},
            "max_value": {"type": "number", "label": "最大值"},
        },
    },
    # 五、枚举值与参照完整性校验
    {
        "expectation_type": "expect_column_values_to_be_in_set",
        "display_name": "值集合检查",
        "category": "枚举值与参照完整性校验",
        "description": "检查列值是否在指定集合内",
        "parameters_schema": {"value_set": {"type": "array", "label": "允许值列表"}},
    },
    {
        "expectation_type": "expect_column_values_to_be_in_type_list",
        "display_name": "类型列表检查",
        "category": "枚举值与参照完整性校验",
        "description": "检查列值类型是否在指定列表内",
        "parameters_schema": {"type_list": {"type": "array", "label": "类型列表"}},
    },
    {
        "expectation_type": "expect_column_values_to_not_be_in_set",
        "display_name": "禁止值检查",
        "category": "枚举值与参照完整性校验",
        "description": "检查列值是否不在指定集合内",
        "parameters_schema": {"value_set": {"type": "array", "label": "禁止值列表"}},
    },
    # 六、排序与序列校验
    {
        "expectation_type": "expect_column_values_to_be_increasing",
        "display_name": "递增检查",
        "category": "排序与序列校验",
        "description": "检查列值是否严格递增",
        "parameters_schema": {},
    },
    {
        "expectation_type": "expect_column_values_to_be_decreasing",
        "display_name": "递减检查",
        "category": "排序与序列校验",
        "description": "检查列值是否严格递减",
        "parameters_schema": {},
    },
    {
        "expectation_type": "expect_column_values_to_be_non_decreasing",
        "display_name": "非递减检查",
        "category": "排序与序列校验",
        "description": "检查列值是否非递减（允许相等）",
        "parameters_schema": {},
    },
    {
        "expectation_type": "expect_column_values_to_be_non_increasing",
        "display_name": "非递增检查",
        "category": "排序与序列校验",
        "description": "检查列值是否非递增（允许相等）",
        "parameters_schema": {},
    },
    # 七、跨列与业务规则校验
    {
        "expectation_type": "expect_column_pair_values_to_be_equal",
        "display_name": "双列相等检查",
        "category": "跨列与业务规则校验",
        "description": "检查两列值是否相等",
        "parameters_schema": {
            "column_A": {"type": "string", "label": "列A"},
            "column_B": {"type": "string", "label": "列B"},
        },
    },
    {
        "expectation_type": "expect_column_pair_values_to_be_in_set",
        "display_name": "双列组合集合检查",
        "category": "跨列与业务规则校验",
        "description": "检查两列值组合是否在指定集合内",
        "parameters_schema": {
            "column_A": {"type": "string", "label": "列A"},
            "column_B": {"type": "string", "label": "列B"},
            "value_pairs_set": {"type": "array", "label": "允许的值对列表"},
        },
    },
    {
        "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
        "display_name": "A列大于B列",
        "category": "跨列与业务规则校验",
        "description": "检查A列值是否大于B列值",
        "parameters_schema": {
            "column_A": {"type": "string", "label": "列A"},
            "column_B": {"type": "string", "label": "列B"},
        },
    },
    {
        "expectation_type": "expect_column_pair_values_A_to_be_greater_than_or_equal_to_B",
        "display_name": "A列大于等于B列",
        "category": "跨列与业务规则校验",
        "description": "检查A列值是否大于等于B列值",
        "parameters_schema": {
            "column_A": {"type": "string", "label": "列A"},
            "column_B": {"type": "string", "label": "列B"},
        },
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for rule_data in RULES:
            exists = db.query(BuiltinRule).filter_by(
                expectation_type=rule_data["expectation_type"]
            ).first()
            if not exists:
                db.add(BuiltinRule(**rule_data))
                print(f"  Added: {rule_data['display_name']}")
            else:
                print(f"  Skipped (exists): {rule_data['display_name']}")
        db.commit()
        print(f"\nDone. Total rules in DB: {db.query(BuiltinRule).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
