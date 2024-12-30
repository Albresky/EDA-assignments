<!--
 * Copyright (c) 2024 by Albresky, All Rights Reserved. 
 * 
 * @Author: Albresky albre02@outlook.com
 * @Date: 2024-12-21 20:04:49
 * @LastEditTime: 2024-12-30 14:59:46
 * @FilePath: /EDA-assignments/lab2/floorplan/README.md
 * 
 * @Description: 
-->
# Lab2: Floorplan

## Setup

Install modules from `requirements.txt`

```bash
pip install -r requirements.txt
```

## Run tests

 - Set the params in `./src/config.json`.


```json
{
    "file":{
        "blocks": "../testcases/xerox.block",
        "nets": "../testcases/xerox.nets"
    },
    "sa_params": {
        "iterations": 10000,
        "alpha": 0.5,
        "temperature": 10000
    }
}
```

 - Then, execute the `main.py`

```bash
cd src
python main.py
```

 - The `.output` file and visualized graph will be created under `./src/output/`

```
src/output/
├── floorplan_2024-12-21-20:18:02.output
├── floorplan_2024-12-21-20:18:02.output.png
├── ...
├── floorplan_2024-12-30-14:15:15.output
└── floorplan_2024-12-30-14:15:15.output.png
```
## Documentation

For detailed introduction for this lab, please refer to the [布图 Floorplan 报告.pdf](./doc/布图%20Floorplan%20报告.pdf).

## References

- [1] S. N. Adya and I. L. Markov, "Fixed-outline Floorplanning through Better Local Search," **International Conference on Computer Design (ICCD)**, 2001.
- [2] N. Sherwani, **Algorithms for VLSI Physical Design Automation**, Springer, 2002.
- [3] 丛京生，萨拉费扎德，"芯片布局设计与优化"，**IEEE Design & Test of Computers**，第14卷，第2期，页码12–25，1997年。
- [4] **ChatGPT o1 preview**
