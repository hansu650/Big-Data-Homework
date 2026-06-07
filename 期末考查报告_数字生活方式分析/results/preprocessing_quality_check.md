# Preprocessing Quality Check

## Dataset-Level Checks

- 原始样本量：3500
- 原始字段数：24
- 缺失值总数：0
- 重复行数量：0
- 重复 id 数量：0

## Numeric Range Checks

已检查字段：age, device_hours_per_day, phone_unlocks, notifications_per_day, social_media_mins, study_mins, physical_activity_days, sleep_hours, sleep_quality, productivity_score, digital_dependence_score。

所有检查字段均处于设定合理范围内，检查后未发现需删除记录。

## Engineered Feature Checks

已检查工程特征：social_media_hours, study_hours, notifications_per_device_hour, unlocks_per_device_hour, device_to_sleep_ratio, activity_sleep_interaction, social_to_study_ratio。

全部工程特征已成功生成。

## Feature Selection Evidence

- 分类任务排除泄漏字段：anxiety_score、depression_score、stress_level、happiness_score、focus_score、productivity_score、digital_dependence_score，以及 id 和目标列 high_risk_flag。
- 回归任务不使用 high_risk_flag、心理状态 outcome 字段，以及另一个 outcome 目标变量。
- 聚类任务只使用数字行为与生活习惯数值特征；人口背景、设备类别和结果变量只用于聚类后画像解释。

## Handling Strategy

本次 Stage 2.5 仅补充质量检查证据，不重新设计实验，不删除原始数据，不改变分类、回归、聚类主实验指标。
