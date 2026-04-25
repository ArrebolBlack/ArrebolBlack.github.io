<!--
  Blog Post Template / 博客文章模板
  ================================

  使用步骤：
  1. 复制 _template/ 整个文件夹，重命名为你的文章 slug（英文、短横线分隔）
     例：cp -r _template/ my-new-post/
  2. 将文章配图放入 images/ 子目录
  3. 编辑 post.md，替换下方所有占位内容
  4. 在 config.json 的 "blog" 数组中添加一条记录：

     {
       "date": "2026-05-01",
       "title": "My Blog Post Title",
       "summary": "One-line summary shown on the blog card.",
       "image": "blog_src/my-new-post/images/cover.png",
       "tags": ["Tag1", "Tag2"],
       "file": "blog_src/my-new-post/post.md"
     }

     - image: 封面图路径（有图填，无图留空 ""）
     - file:  指向 post.md 的路径
  5. 运行 python build.py
-->

## Introduction

在这里写文章开头。支持 **加粗**、*斜体*、`行内代码` 和 [超链接](https://example.com)。

## Main Content

### 插入图片

将图片放到同级 `images/` 目录，用相对路径引用：

![图片说明](images/figure1.png)

### 列表

- 要点一
- 要点二
- 要点三

### 引用

> 这是一段引用。适合放重要结论或名言。

### 代码块

```python
print("Hello, world!")
```

## Summary

文章末尾总结或展望。
