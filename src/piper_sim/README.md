# piper_sim

[English](#english) | [日本語](#japanese)

![ubuntu](https://img.shields.io/badge/Ubuntu-22.04-orange.svg)
|ROS |STATE|
|---|---|
|![ros](https://img.shields.io/badge/ROS-humble%2Fjazzy-blue.svg)|![Pass](https://img.shields.io/badge/Pass-blue.svg)|

---

<a name="english"></a>
## 🇬🇧 English

### 1. Gazebo Simulation

#### 1.0 Environment Setup

```bash
sudo apt update
sudo apt install gazebo ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control ros-humble-ros2-control ros-humble-ros2-controllers
# For ROS 2 Jazzy, ensure compatible packages are installed (e.g., ros-jazzy-ros-gz-*)
```

#### 1.1 Piper Gazebo Simulation (With Gripper)

Run Gazebo simulation:

```bash
cd piper_ros
source install/setup.bash
```

```bash
ros2 launch piper_gazebo piper_gazebo.launch.py
```

**With Orbbec Camera (Updated):**

To launch with the Orbbec camera attached, use the following command. The default position has been optimized for the best view.

```bash
ros2 launch piper_gazebo piper_gazebo.launch.py \
  use_orbbec_camera:=true \
  orbbec_parent_link:=gripper_base
```

*Note: Default `orbbec_xyz` is now `"-0.05 0.025 0"` and `orbbec_rpy` is `"0 -1.57 0"`. You can override these if needed.*

**Verifying Camera Data:**
```bash
ros2 topic hz /orbbec/rgb/image
```

#### 1.2 Piper Gazebo Simulation (No Gripper)

```bash
ros2 launch piper_gazebo piper_no_gripper_gazebo.launch.py
```

*Note: If controlling via MoveIt, launch Gazebo first, then launch MoveIt using `piper_moveit.launch.py` (not demo.launch.py).*

---

### 2. Mujoco Simulation

#### 2.1 Installation (Mujoco210 & mujoco-py)

##### 1. Install MuJoCo
1. Download [mujoco210](https://github.com/google-deepmind/mujoco/releases/download/2.1.0/mujoco210-linux-x86_64.tar.gz)
2. Extract:
   ```bash
   mkdir ~/.mujoco
   tar -zxvf mujoco210-linux-x86_64.tar.gz -C ~/.mujoco
   ```
3. Add to env:
   ```bash
   echo "export LD_LIBRARY_PATH=~/.mujoco/mujoco210/bin:\$LD_LIBRARY_PATH" >> ~/.bashrc
   source ~/.bashrc
   ```
4. Test:
   ```bash
   cd ~/.mujoco/mujoco210/bin
   ./simulate ../model/humanoid.xml
   ```

##### 2. Install mujoco-py
```bash
git clone https://github.com/openai/mujoco-py.git
cd mujoco-py
pip3 install -U 'mujoco-py<2.2,>=2.1'
pip3 install -r requirements.txt
python3 setup.py install
sudo apt install libosmesa6-dev patchelf
```

Add env var:
```bash
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/nvidia" >> ~/.bashrc
source ~/.bashrc
```

#### 2.2 Piper Mujoco Simulation

**With Gripper:**
```bash
ros2 run piper_mujoco piper_mujoco_ctrl.py
```

**Without Gripper:**
```bash
ros2 run piper_mujoco piper_no_gripper_mujoco_ctrl.py
```

 Control parameters can be found in `../piper_description/mujoco_model/`.

---

<a name="japanese"></a>
## 🇯🇵 日本語

### 1. Gazebo シミュレーション

#### 1.0 環境設定

```bash
sudo apt update
sudo apt install gazebo ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control ros-humble-ros2-control ros-humble-ros2-controllers
# ROS 2 Jazzyの場合は、対応するパッケージ（例: ros-jazzy-ros-gz-*）を確認してください。
```

#### 1.1 Piper Gazebo シミュレーション (グリッパーあり)

シミュレーションの起動:

```bash
cd piper_ros
source install/setup.bash
```

```bash
ros2 launch piper_gazebo piper_gazebo.launch.py
```

**Orbbecカメラの使用（更新情報）:**

Orbbecカメラを装着して起動する場合、以下のコマンドを使用します。最適な位置調整済みのデフォルト値が適用されます。

```bash
ros2 launch piper_gazebo piper_gazebo.launch.py \
  use_orbbec_camera:=true \
  orbbec_parent_link:=gripper_base
```

*注: デフォルトの `orbbec_xyz` は `"-0.05 0.025 0"`、`orbbec_rpy` は `"0 -1.57 0"` に設定されています。必要に応じて上書き可能です。*

**カメラデータの確認:**
```bash
ros2 topic hz /orbbec/rgb/image
```

#### 1.2 Piper Gazebo シミュレーション (グリッパーなし)

```bash
ros2 launch piper_gazebo piper_no_gripper_gazebo.launch.py
```

*注: MoveItで制御する場合は、先にGazeboを起動し、その後に `piper_moveit.launch.py` を使用してMoveItを起動してください（demo.launch.pyではありません）。*

---

### 2. Mujoco シミュレーション

#### 2.1 インストール (Mujoco210 と mujoco-py)

##### 1. MuJoCo のインストール
1. [mujoco210](https://github.com/google-deepmind/mujoco/releases/download/2.1.0/mujoco210-linux-x86_64.tar.gz) をダウンロード
2. 解凍:
   ```bash
   mkdir ~/.mujoco
   tar -zxvf mujoco210-linux-x86_64.tar.gz -C ~/.mujoco
   ```
3. 環境変数の追加:
   ```bash
   echo "export LD_LIBRARY_PATH=~/.mujoco/mujoco210/bin:\$LD_LIBRARY_PATH" >> ~/.bashrc
   source ~/.bashrc
   ```
4. テスト:
   ```bash
   cd ~/.mujoco/mujoco210/bin
   ./simulate ../model/humanoid.xml
   ```

##### 2. mujoco-py のインストール
```bash
git clone https://github.com/openai/mujoco-py.git
cd mujoco-py
pip3 install -U 'mujoco-py<2.2,>=2.1'
pip3 install -r requirements.txt
python3 setup.py install
sudo apt install libosmesa6-dev patchelf
```

環境変数の追加:
```bash
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/nvidia" >> ~/.bashrc
source ~/.bashrc
```

#### 2.2 Piper Mujoco シミュレーション

**グリッパーあり:**
```bash
ros2 run piper_mujoco piper_mujoco_ctrl.py
```

**グリッパーなし:**
```bash
ros2 run piper_mujoco piper_no_gripper_mujoco_ctrl.py
```

制御パラメータは `../piper_description/mujoco_model/` にあります。
