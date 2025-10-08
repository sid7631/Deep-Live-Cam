# Building the Deep Live Cam macOS App Bundle Locally

The repository ships with a [`py2app`](https://py2app.readthedocs.io/) setup script (`setup_mac.py`) that packages
`run.py` and the required resources into a self-contained `Deep Live Cam.app` bundle.  This guide walks through the
entire process on a clean macOS installation.

> **Tested on:** macOS Sonoma 14 and Ventura 13 on both Intel and Apple Silicon hardware.

## 1. Prerequisites

1. **Update macOS** – Install the latest available macOS updates from *System Settings → General → Software Update*.
2. **Install Xcode Command Line Tools** – Required for compiling native wheels that `pip` may download.
   ```bash
   xcode-select --install
   ```
3. **Install Homebrew** – Skip this step if Homebrew is already available.
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
4. **Install Python and Tk** – Deep Live Cam works best on Python 3.11 for the standard CPU build.  On Apple Silicon you
   can still use Python 3.10 if you plan to run with the CoreML execution provider.  Pick one of the following:
   - **CPU / GPU (recommended):**
     ```bash
     brew install python@3.11 python-tk@3.11
     ```
   - **CoreML (Apple Silicon only):**
     ```bash
     brew install python@3.10 python-tk@3.10
     ```

   Homebrew prints the `PATH` snippet that activates the selected Python version.  Follow the instructions it outputs,
   then verify the interpreter:
   ```bash
   python3 --version
   which python3
   ```

   > ℹ️  If the exact `python-tk@<version>` formula is unavailable on your system, install the generic package instead:
   > ```bash
   > brew install python-tk
   > ```

## 2. Clone the Repository and Prepare the Environment

```bash
# Clone the project
git clone https://github.com/hacksider/Deep-Live-Cam.git
cd Deep-Live-Cam

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade the installer tooling and install dependencies
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Install py2app inside the same environment
pip install py2app
```

If you ever need to start over, run `deactivate` and delete the `venv` folder before recreating the environment.

## 3. Download the Model Weights

Download the required model files and place them in the `models/` directory before packaging:

- [`GFPGANv1.4.pth`](https://huggingface.co/hacksider/deep-live-cam/resolve/main/GFPGANv1.4.pth)
- [`inswapper_128_fp16.onnx`](https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx)

You can either download them manually or run the project once with `python run.py`; the program will fetch any missing
weights automatically.

## 4. Build the `.app` Bundle

With the virtual environment still activated:

```bash
python setup_mac.py py2app
```

The build may take a few minutes.  A successful run produces the following artefacts:

- `dist/Deep Live Cam.app` – The distributable application bundle.
- `build/` – Temporary build products (safe to delete after verifying the app).

## 5. Test the Generated Application

1. Double-click `dist/Deep Live Cam.app`.  The first launch may take a moment while macOS verifies the bundle.
2. If the window fails to appear, open the log file at `dist/Deep Live Cam.app/Contents/MacOS/Deep Live Cam` from the
   terminal to see Python stack traces:
   ```bash
   ./dist/Deep\ Live\ Cam.app/Contents/MacOS/Deep\ Live\ Cam
   ```
3. Verify that the GUI loads and that the models can be selected.  The app uses the same configuration files as the
   source checkout.

## 6. Optional: Sign and Notarize for Distribution

For personal use you can run the unsigned bundle directly.  If you plan to distribute the app, sign it with your
Developer ID certificate and submit it for notarization:

```bash
codesign --force --deep --sign "Developer ID Application: Your Name" dist/Deep\ Live\ Cam.app
xcrun notarytool submit dist/Deep\ Live\ Cam.app --keychain-profile "AC_PASSWORD" --wait
```

After notarization completes, staple the ticket:

```bash
xcrun stapler staple dist/Deep\ Live\ Cam.app
```

## 7. Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ImportError: No module named _tkinter` | Ensure `python-tk@3.10` or `python-tk@3.11` is installed and that you are using the corresponding Homebrew Python in your virtual environment. |
| Build fails with `ModuleNotFoundError` | Re-run `pip install -r requirements.txt` inside the virtual environment and confirm it is activated. |
| App launches but cannot find models | Check that `models/` sits next to `run.py` before invoking the build script so `py2app` bundles the weights. |
| macOS blocks the app as "unverified" | Control-click the app, choose *Open*, then confirm.  Signing/notarization removes the warning for other users. |

With these steps you have a reproducible, local workflow for packaging Deep Live Cam into a macOS application bundle.
