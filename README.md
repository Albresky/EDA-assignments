<!--
 * @Descripttion: Edit your description
 * @Author: Albresky
 * @Date: 2024-11-28 13:56:02
 * @LastEditors: Albresky
 * @LastEditTime: 2024-12-13 16:38:17
-->
# BUPT 数字 EDA 理论基础 | Lab 实验

# Intro

本 repo 是 BUPT 数字 EDA 理论基础课程的实验内容，主要包括以下几个部分：

 - Lab1.1: Matrix Multiplication
    - `unroll`, `pipeline`, `array partition`, etc. HLS pragma
    - Block-level parallelism in MM with `dataflow` HLS pragma

 - Lab2.2: Floorplan Algorithm
    - ~~BStarTree-based(decrepated)~~
    - *Simulated Annealing* optimization
    - Tools implemented:
        - parser
        - visualizer
        - floorplanner


# Demo

<table>
  <tr>
    <th>
    <img src="images/lab1.1_original_cycles.png" height="200">
    </th>
    <th>
    <img src="images/lab1.1_unrolled_cycles.png" height="200">
    </th>
  </tr>
  <tr>
    <td>
    <img src="images/lab1.2_floorplan_results1_visualized.png" height="400">
    </td>
    <td>
    <img src="images/lab1.2_floorplan_results2_visualized.png" height="400">
    </td>
</tr>
</table>

# About

第一次写 Floorplan，轻喷，LOL...