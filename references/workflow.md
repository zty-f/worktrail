# 来源与按需产出配置

## 两个独立选择

用户可分别选择资料来源和产出。不能因为选平台就要求全部安装，也不能因为做绩效就默认生成完整文档/PPT。已经明确的偏好直接沿用；未明确产出时默认summary。

workflow.json保存选择，brief.json保存身份、岗位、项目、时间和报告场景，sources.json只保存平台上已选文档的定位。三者都不保存OAuth凭据。

```json
{
  "schema_version": "1.0",
  "source": {"mode": "local", "local_folders": ["/absolute/materials"]},
  "outputs": ["summary"]
}
```

source.mode为local/feishu/dingtalk/wecom/mixed。平台单来源设置platform_config为实际sources.json绝对路径；mixed可同时列local_folders及platform_config。平台配置里出现未选平台会拒绝执行，不自动扩展范围。未选具体文档时collect会停在配置阶段，不进行空范围搜索。

```bash
python scripts/review.py configure /absolute/workspace --source local --local-folder /absolute/materials --outputs summary
python scripts/review.py configure /absolute/workspace --source mixed --local-folder /absolute/materials --sources-config /absolute/workspace/sources.json --outputs summary,evidence
```

configure只保存选择，不采集、不安装、不登录。collect才按范围读取。切换范围时未选来源停用，历史保留；本人manual/journal补充保留。旧事实若还引用停用来源会失效，需要Agent重新核对或排除，避免旧资料混入新总结。

## 产出列表

summary/report/evidence/docx/pdf/pptx/self-eval/speaker-notes，可多选，all为明确全选。单次build --outputs覆盖本次导出，不改变持久选择；configure --outputs修改持久选择。

每次成功output只保留本次所选的文件及manifest。构建中间文件在builds的私有运行目录，未选格式不放进output。用户只要PDF时，Word是私有渲染中间件；只要PPT时不运行Word/PDF导出；只要总结或证据时不检查PPT运行时。讲述提示可单独生成，文件不证明已经制作PPT。

manifest包含requested_outputs/generated_outputs及选择指纹；verify只要求所选格式存在。未选PPT的editable_pptx_created=false是正常结果，不表示总结失败。旧--skip-ppt只保留作开发兼容；如果原请求有PPT但跳过，verify不会把它标为完整完成。

## Agent怎样使用

1. 从用户话语确定来源与产出，缺来源才问；“只总结工作内容和成效”映射summary，不强行问演讲时长或模板。
2. 新建用户独立工作区，保存workflow、brief；需要平台时仅走对应安装授权说明。
3. collect后实际阅读evidence-packet，按合同逐条记录个人/团队、日期、完成状态、引用、语义复核。
4. analyze集中确认会影响结论的缺口；只选轻量总结也必须保留相同的证据约束。
5. 仅对所选格式做doctor/build/verify及必要视觉验收；返回本次真实文件，说明缺口，不假装已生成未选格式。

平台目录浏览、文件候选选择与类型路由由Agent使用官方CLI完成；它们没有被描述成collect内置的跨三平台任意目录递归同步。
