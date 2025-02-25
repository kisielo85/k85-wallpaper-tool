# k85 wallpaper tool

a simple wallpaper tool for multiple monitors that takes into account different screen sizes and spaces between them
<br><br>
*note: currently it does not work for monitors stacked vertically*

## Installation

### Option 1 (for Windows only)

1. go to the [Releases](https://github.com/kisielo85/k85-wallpaper-tool/releases) page
2. download and run the latest .exe file

### Option 2

1. Install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Python](https://www.python.org/downloads/)
2. Clone repository

   ```cmd
   git clone https://github.com/kisielo85/k85-wallpaper-tool
   ```
   ```cmd
   cd k85-wallpaper-tool
   ```
3. Create virtual enviroment (optional)

   ```bash
   python -m venv venv
   ```
   **Windows**

   ```cmd
   venv\Scripts\activate
   ```
   **Linux**

   ```bash
   source venv/bin/activate
   ```
4. Install requirements

   ```bash
   pip install -r requirements.txt
   ```
5. Run script

   ```bash
   python main.py
   ```
