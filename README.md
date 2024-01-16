# Image Mixer

In this project, the goal is to design and implement a desktop program that illustrates the significance of magnitude and phase components, emphasizing frequency contributions within a 2D signal, particularly images. The software incorporates various features to enhance user interaction and customization.

<div align="center">
  <img src="data/screenshot.png" />
</div>

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contributors](#contributors)

## Features

- **Open 4 Images:** Load Images visualization and processing.

- **Visualize image components:** Visualize the 4 components of each image: Magnitude, Phase, Real, and Imaginary.

- **Real time brightness and contrast control:** Adjust the brightness and contrast to meet your requirements.

- **Image Mixer:** Create a new image by mixing either phase and magnitude or imaginary and real in an intuitve way.

- **Regions Mixer:** Mask the regions you want to mix with a single click and drag.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- PyQt6

### Installation

1. Clone this repository to your local machine.

```bash
git clone https://github.com/Bodykudo/Image-Mixer.git
```

2. Install the required dependencies.

```bash
pip install requirements.txt
```

3. Run the application.

```bash
python main.py
```

## Usage

1. **Open Images:**

   - Double click the "image port" to select an image for visualization.

2. **Brightness and Contrast Control:**

   - Scroll your cursor horizontally for contrast control and vertically for brightness control.

3. **Image Mixer:**

   - Choose the mixing mode magnitude/phase or real/imaginary.
   - Use sliders to adjust the components weights percentages.
   - Click "Convert" to start mixing.

4. **Regions Mixer:**

   - Choose the inner or outer mode then use the mouse to select your ROI.

## Contributors
<table>
  <tr>
    <td align="center">
    <a href="https://github.com/Bodykudo" target="_black">
    <img src="https://avatars.githubusercontent.com/u/17731926?v=4" width="150px;" alt="Abdallah Magdy"/>
    <br />
    <sub><b>Abdallah Magdy</b></sub></a>
    <td align="center">
    <a href="https://github.com/abduelrahmanemad" target="_black">
    <img src="https://avatars.githubusercontent.com/u/104274128?v=4" width="150px;" alt="Abdelrahman Emad"/>
    <br />
    <sub><b>Abdelrahman Emad</b></sub></a>
    </td>
    </td>
    <td align="center">
    <a href="https://github.com/MohamedAlaaAli" target="_black">
    <img src="https://avatars.githubusercontent.com/u/94873742?v=4" width="150px;" alt="Mohamed Alaa"/>
    <br />
    <sub><b>Mohamed Alaa</b></sub></a>
    </td>
    <td align="center">
   <td align="">
    <a href="https://github.com/Medo072" target="_black">
    <img src="https://avatars.githubusercontent.com/u/83141866?v=4" width="150px;" alt="Mohamed Ibrahim"/>
    <br />
    <sub><b>Mohamed Ibrahim</b></sub></a>
    </td>
    </tr>
 </table>

---

Enjoy working with Image Mixing!
