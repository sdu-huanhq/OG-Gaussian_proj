# 图片与视频素材

网页展示素材保存在此目录，通过 `../js/content.js` 配置。
配置中的所有文件路径均相对于 `paper_project/index.html`。

当前页面使用以下素材：

- `static/media/revised-20261117/method/overview.png`：由新版 `overview_mask3.pdf` 导出的静态方法总览图。
- `static/media/simulation/pour-water.webp`：倒水任务的仿真对比图。
- `static/media/simulation/place-teabag.webp`：放置茶包任务的仿真对比图。
- `static/media/simulation/place-atomizer.webp`：放置喷雾瓶任务的仿真对比图。
- `static/media/simulation/lower-cover.webp`：合上笔记本电脑任务的仿真对比图。
- `static/media/simulation/close-drawer.webp`：关闭抽屉任务的仿真对比图。
- `static/media/revised-20261117/real-world/pour-water.mp4`：倒水，9.792 秒。
- `static/media/revised-20261117/real-world/place-teabag.mp4`：放置茶包，14.333 秒。
- `static/media/revised-20261117/real-world/place-atomizer.mp4`：放置喷雾瓶，12.875 秒。
- `static/media/revised-20261117/real-world/lower-cover.mp4`：合上笔记本电脑，17.708 秒。
- `static/media/revised-20261117/real-world/close-drawer.mp4`：关闭抽屉，9.833 秒。
- `static/media/revised-20261117/exploratory/multiple-references.mp4`：多参考场景倒水，12.667 秒，使用 Pour Water 任务权重。
- `static/media/revised-20261117/exploratory/unseen-tasks.mp4`：未见任务将水壶放入抽屉，11.750 秒，使用 Place Teabag 任务权重。

第二次执行的视频及同名 JPG 封面保存在 `static/media/revised-20261117-second-executions/real-world/`：

- `pour-water-2.mp4`：11.833 秒。
- `place-teabag-2.mp4`：15.125 秒。
- `place-atomizer-2.mp4`：13.458 秒。
- `lower-cover-2.mp4`：14.583 秒。
- `close-drawer-2.mp4`：10.625 秒。

每张仿真图包含四种方法和两组示例，原局部放大标记保留。
所有当前视频均从新版 `demo_revised.mp4` 截取，保留原片的 5× 倍速和音轨，另有同名 JPG 封面。
五个真机任务各显示两次执行，在每个任务标签下并排展示两个独立视频窗口。两个探索性实验视频只包含成功演示，不包含后续失败案例。
第一段视频和探索性实验的裁剪记录见 `revised-20261117/processing.json`；第二段视频的记录见 `revised-20261117-second-executions/processing.json`。

网页探索性实验标题为 Exploratory Experiments，两个子标题为
Multi-Reference Configuration 和 Unseen Task Configuration。
旧版 `real-world/` 视频及封面、`method/overview.png` 和空的 `toy-cases/` 占位目录已清理。
`method/overview_mask3.pdf` 是不同于根目录新版图的旧版本，仍保留；旧版 `processing.json` 作为导出记录保留。

旧版原始 PDF 和完整 MP4 已原样归档至网页目录之外的
`paper_project_sources/20261106_230315/`（相对于仓库根目录），避免身份元信息随网页公开。
新版原件位于 `paper_project/overview_mask3.pdf` 和 `paper_project/demo_revised.mp4`，不直接链接到页面。
更新素材时，可将匿名处理后的图片和视频放入新的子目录。
路径为空时，页面显示占位区，不会请求不存在的文件。
未使用的原模板示例素材及第三方库已清理。

完整配置说明见 [项目 README](../../README.md)。
