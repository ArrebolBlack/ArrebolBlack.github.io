## Introduction

本项目面向机器人精细操作中触觉信息智能感知的难题，提出基于铝酸锶（SrAl₂O₄）热释光效应的多模态视触觉传感器 **SATac**，并结合深度生成模型与具身智能方法，构建从传感器设计、信息解耦、遥操作反馈到自主操作的完整技术链路。

![研究背景：多模态触觉感知](images/background_nobel_prize.png)

人类皮肤中同时分布着温度感受器（约100~140个/cm²）和机械感受器（约200个/cm²），赋予人类同时感知温度和力的能力。然而，现有视触觉传感器（如GelSight）虽可高分辨率力感知，但难以同时感知温度；热阻式传感器虽能测温但分辨率低。

![相关工作对比](images/related_work_vision_tactile.png)

SATac 创新性地利用铝酸锶在 UVC（280nm）激发下发出 520nm 荧光的热释光效应，首次在单一传感器上实现了**温度分布、压强和剪切力**三种模态的高分辨率同时感知。

## SATac 传感器设计

### 传感原理

SATac 的核心是双光场设计：UV 光场（280nm）和荧光光场（520nm）同时被摄像头捕获，通过引导滤波算法解耦出三种模态。

![SATac 传感概念](images/satac_concept.png)

- **模态 1 — 温度分布场**：SA 荧光强度随温度变化
- **模态 2 — 法向力场**：SA 膜 + marker 点的形变
- **模态 3 — 剪切力场**：marker 点的位移方向与幅度

![双光场设计](images/satac_dual_light_field.png)

SA 膜由铝酸锶荧光粉与硅胶混合涂覆而成，表面带有 marker 点用于力感知：

![SA 膜与 marker 点](images/satac_sensing_layer.png)

### 硬件结构

传感器由摄像头、UVC-LED+滤光片、透明支撑板、PDMS 弹性体、SA 膜和外壳组成：

![传感器 3D 模型对比（旧版 vs 新版）](images/sensor_3d_model_comparison.png)

通过重新设计，传感器尺寸大幅缩小，可部署于 AG95 二指夹爪：

![传感器部署在夹爪上](images/sensor_on_gripper.png)

SA 材料在 UVC 激发下产生热释光效应，荧光强度随温度变化：

![SA 荧光粉与热释光效应](images/sa_powder_thermoluminescence.png)

## 传感器优化

### 光路系统优化

光路优化是提升传感性能的关键，涉及从紫外光源到荧光采集的完整链路。

**紫外光源优化：** 不同波长 LED 的充能效果差异大，波长增加充能变快但干扰摄像头观察：

![UV LED 波长对比](images/uv_led_wavelength_comparison.png)

**PDMS 弹性体优化：** 系统研究了固化温度和固化剂比例对紫外透射率的影响：
- 固化温度越高，透射率越高
- 固化剂比例越大（越硬），透射率越高

![PDMS 固化温度影响](images/pdms_curing_temp.png) ![PDMS 比例影响](images/pdms_ratio.png)

对比了不同厚度的 PDMS（5mm vs 10mm）：

![PDMS 10mm](images/pdms_10mm.png) ![PDMS 5mm](images/pdms_5mm.png)

**支撑板材料优化：** 从亚克力（5mm，320nm 透过）更换为紫外高透石英（1mm，280nm 透过），大幅提升 UV 透过率：

![亚克力透射谱](images/acrylic_transmission.png) ![石英透射谱](images/quartz_transmission.png)

**LED+滤光片组合优化：**

![LED + 滤光片](images/led_filter.png)

### ESP32 自动充能电路

设计了基于 ESP32 的紫外 LED 自动充能控制电路，包含 PWM 调光、Boost 升压和 FET 开关控制，替代手动充能：

![ESP32 电路设计](images/esp32_circuit_diagram.png)

支持占空比 10%~100% 可调的 PWM 调光：

![PWM 占空比控制](images/pwm_duty_10.png)

自动充能实现了稳定的一次温度感知周期控制：

![自动充能效果对比](images/auto_charging_result.png)

## 温度分布解耦算法

### 问题与方法

双光场设计中，UV 光场区域的 marker 点遮挡了荧光信息，需要通过图像修复补全空洞区域。系统对比了多种深度生成模型：

![数据处理流程](images/algorithm_workflow.png)

| 模型 | 类型 | 特点 |
|------|------|------|
| UNet → Complex UNet | 编码器-解码器 | 基线方法 |
| GL-GAN → SN-GAN | 生成对抗网络 | 全局-局部判别器 + 谱归一化 |
| Patch-based DDPM | 去噪扩散模型 | 高分辨率处理 |
| AE → AE + Attention | 自编码器 | 引入注意力机制 |
| **VQ-VAE** | 向量量化 VAE | **最优结果** |

### 最佳方案：VQ-VAE

VQ-VAE 通过离散编码本实现高质量修复，在 marker 点空洞区域生成了语义合理、边界平滑的结果：

![VQ-VAE 修复结果](images/vqvae_best_result.png)

VQ-VAE 修复后的图像与引导滤波结合，实现了温度场与 UV 光场的完整分离。

## 传感性能验证

### 温度分布感知

在 50°C ~ 200°C 范围内验证了温度分布感知能力：

![温度感知范围 50-200°C](images/temperature_sensing_range.jpg)

对比了不同滤波方法，引导滤波效果最佳：

| 中值滤波 | 高斯滤波 | 引导滤波 |
|---------|---------|---------|
| ![中值滤波](images/filter_median.jpg) | ![高斯滤波](images/filter_gaussian.jpg) | ![引导滤波](images/filter_guided.jpg) |

### 压强与剪切力感知

在 2N ~ 8N 力范围内验证了压强和剪切力感知：

![压强感知](images/pressure_sensing.png) ![剪切力感知](images/shear_force_sensing.png)

### 应用场景

完成发光物体接触检测、金属物体接触检测和热空气检测等应用演示：

![热物体检测](images/application_hot_object.png) ![金属物体检测](images/application_metal_object.png)

## 机器人遥操作平台

### 手眼标定

基于 ROS 完成了 eye-in-hand 手眼标定，标定误差 < 1cm：

![手眼标定结果](images/hand_eye_calibration_result.png) ![标定可视化](images/hand_eye_calibration_visual.png)

### 遥操作控制

实现了 3D 游戏手柄和 VR 手柄的 6 自由度位姿遥操作：

![手柄与 VR 遥操作](images/teleoperation_gamepad_vr.jpg)

### 触觉反馈装置

制作了多模态触觉反馈装置，包含编码器位置反馈和被动阻尼力觉反馈：

![触觉反馈装置](images/haptic_feedback_device.png) ![反馈机构](images/haptic_feedback_mechanism.png)

## Octo 具身智能模型复现与部署

### Octo 架构

Octo 是基于 Transformer 的通用机器人操作策略模型（VLA），架构为 **Input Tokenizers + Transformer Backbone + Readout Heads**：

![Octo 模型架构](images/octo_architecture.png)

- **语言输入**：tokenized → 预训练 Transformer → language embedding tokens
- **图像输入**：浅层 CNN → patches → 图像 tokens（ViT）
- **动作输出**：Diffusion Action Head，从高斯噪声逐步去噪解码为动作序列

### 仿真与实机环境

**PyBullet 仿真环境：** UR5/Panda + Robotiq 85/140 夹爪，兼容 Gym 和 dm_env 格式。

![仿真环境](images/simulation_environment.png)

**实机环境：** 分别搭建了 UR5 和 UR3 两套实机平台。

![UR5 实机环境](images/real_robot_setup_ur5.png) ![UR3 实机环境](images/real_robot_setup_ur3.png)

### 数据集

基于 RLDS/TFDS 格式采集了 **10 个数据集、98 个 episodes、约 3.3GB** 数据。数据集已上传至 [HuggingFace](https://huggingface.co/datasets/JiaqiYin/octo_ur5_dataset)。

### 实机 Rollout 结果

**UR5（Task: put cube on plate）：** 最佳模型在 500k 步微调后可成功完成任务：

![UR5 最佳结果](images/ur5_best_result.png)

**仿真 Rollout：** 在 PyBullet 环境中验证了模型性能：

![仿真 Rollout](images/sim_rollout_result.png)

### Mode Collapse 发现

在 UR5 实验中发现：在已训练的最佳模型基础上继续微调，即使仅增加 50k 步，也会导致 **模式崩溃**（Mode Collapse），且继续训练时间越长崩溃越严重：

| 额外训练 50k 步 | 额外训练 300k 步 |
|----------------|-----------------|
| ![50k 步崩溃](images/mode_collapse_50k.png) | ![300k 步崩溃](images/mode_collapse_300k.png) |

> 从头训练 100k 步无法完成任务，但持续微调已训练模型会导致 mode collapse。这一发现对 Octo 模型的微调策略具有重要参考价值。

## 多模态触觉具身智能任务

最终目标是构建多模态触觉具身智能系统，实现"拿起两杯水中的热水"等任务：

![多模态任务概览](images/multimodal_task_overview.png)

相关工作表明触觉信息（力+温度）有助于液体倾倒等精细操作任务。未来将把温度模态接入 Octo 模型，实现力+温度双模态感知的自主操作。

## Summary

本项目完成了基于热释光效应的多模态视触觉传感器 SATac 的设计、优化与验证，系统研究了深度生成模型在温度分布解耦中的应用，搭建了完整的机器人遥操作控制平台，并成功复现和部署了 Octo 具身智能模型。关键成果包括：

- **SATac 传感器**：通过光路优化和 ESP32 自动充能电路，实现温度分布（50°C~200°C）、压强（2N~8N）和剪切力三模态高分辨率同时感知
- **VQ-VAE 图像补全**：在 6 种深度生成模型中取得最优的 marker 点空洞修复效果
- **Octo 实机部署**：在 UR5/UR3 上完成完整的数据采集、微调和 Rollout 流程，并发现 mode collapse 现象

> **代码开源**：https://github.com/ArrebolBlack/Octo
> **数据集**：[HuggingFace](https://huggingface.co/datasets/JiaqiYin/octo_ur5_dataset)
