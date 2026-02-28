The following information in this folder was provided by our sponsors the UVAHealth Team:

# 🧬 Synthetic FHIR Data Generator
A Python module for generating realistic, standards‑compliant synthetic FHIR resources.

## 📌 1. Overview
This project provides a flexible, extensible engine for generating synthetic FHIR (Fast Healthcare Interoperability Resources) data. It is designed for testing, prototyping, analytics pipelines, sandbox environments, and educational use—without exposing any real patient information.

The generator aligns data to US-Core profile (v8.0.1: STU8) based on FHIR (HL7® FHIR® Standard) R4. This is the canonical version at https://hl7.org/fhir/us/core/ as of 02.25.2026.

## ✨ 2. US Core (v8.0.1: STU8) based on FHIR (HL7® FHIR® Standard) R4  
- Home/Landing-page: https://hl7.org/fhir/us/core/
- Table of Contents: https://hl7.org/fhir/us/core/toc.html
- General Requirements: https://hl7.org/fhir/us/core/general-requirements.html
- FHIR artifacts defined as part of this implementation guide: https://hl7.org/fhir/us/core/artifacts.html
- Download US Core profile package v8.0.1: 
  - NPM Package in Links at https://hl7.org/fhir/us/core/history.html
  - OR Package(compressed folder) at https://hl7.org/fhir/us/core/downloads.html
- Resource and Dependencies: https://build.fhir.org/ig/HL7/US-Core/branches/8.0.1/ImplementationGuide-hl7.fhir.us.core.html
- SMART on FHIR Obligations and Capabilities: https://hl7.org/fhir/us/core/scopes.html

<!--
- https://hl7.org/fhir/R4/validation.html
- https://hl7.org/fhir/R4/http.html#search
- https://hl7.org/fhir/smart-app-launch/STU2.2/


- https://terminology.hl7.org/7.0.1/
- https://terminology.hl7.org/7.0.1/toc.html
- https://terminology.hl7.org/7.0.1/index.html
- https://terminology.hl7.org/7.0.1/codesystems.html

-->


## ✨ 3. Features
- Generates FHIR R4 files
- Supports core resource types (Patient, Encounter, Observation, Condition, etc.)
- Deterministic or random data generation
- Export to JSON
- Optional validation using FHIR validators (https://github.com/hapifhir/org.hl7.fhir.core/releases) or fallback python-based validator.

## 🏗️ 4. Project Structure
```code
FHIR-Synthetic-Data/
│
├── src/uscore_synth/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── generator.py
│
├── validator/
│   ├── validator_cli.jar
│   ├── package_v8.0.1_R4/
|
├── pyproject.toml
├── set_java_path.ps1
└── README.md
```

## 🔧 5. Requirements
- Python 3.12+
  - poetry, faker
- (Optional) JAVA 17+  
  **JAVA is required to run validation.**

## 🚀 6. Quick Start
Generate a bundle of synthetic data 

### 6.1 Setup python environment
```powershell
 $ poetry install
```

### 6.2 (Optional ) Setup JAVA 
This is only required if you are running the validator.  
- Download JAVA binaries from OPENJDK
- Edit the following lines in `set_java_path.ps1` to set `JAVA/Node` path:
  ```powershell
  $JavaPath = "C:\Users\...\jdk-17.0.18+8\bin"
  $NodePath = "C:\Users\...\node-v24.13.1-win-x64"
  ```
- Set up JAVA path as:
  ```powershell
     set_java_path.ps1
  ```

### 6.3 Generate synthetic data
1. Generate synthetic data with default arguments
   ```powershell
     $ poetry run uscore-synth generate
   ```  

   Deafult arguments are declared in `cli.py`:
   ```python
    gen.add_argument("--start-year", type=int, default=2018)
    gen.add_argument("--end-year", type=int, default=2025)
    gen.add_argument("--mrns-per-year", type=int, default=100)
    gen.add_argument("--workers", type=int, default=8)
    gen.add_argument("--chunksize", type=int, default=10)
    gen.add_argument("--out-root-dir", type=str, default="./out")
    gen.add_argument("--remove-existing-files", type=int, default=1, choices=[0,1])
    gen.add_argument("--seed", type=int, default=42)
    # Validator related - it takes a long time to validate
    gen.add_argument("--validate", type=int, default=0, choices=[0,1]) # validator uses profiles in uscore-root
    gen.add_argument("--validator-path", type=str, default="./validator/validator_cli.jar") # path to validator_cli.jar
    gen.add_argument("--uscore-root", type=str, default="./validator/package_v8.0.1_R4") # path to profiles
   ```  

2. Generate synthetic data with custom arguments
   ```powershell
     $ poetry run uscore-synth generate --workers 1 --mrns-per-year 2 --validate 1
   ```

2. Generate synthetic data and log all output/errors to file `output.log`
   ```powershell
     $ poetry run uscore-synth generate > output.log 2>&1 
   ```

### 6.4 Run validator
1. Create a new `validator` folder at project root folder.
2. Download the latest release of `validator_cli.jar` from https://github.com/hapifhir/org.hl7.fhir.core/releases and place this inside the folder `validator`.
3. Download the `IG Version 8.0.1` `NPM Package` from https://hl7.org/fhir/us/core/history.html. Unzip it, and place it inside the folder `validator`. Rename the unzipped `pacakge` folder to `package_v8.0.1_R4`. 
4. Run validator in windows powershell terminal as:
   ```powershell
     $ poetry run uscore-synth generate --workers 1 --mrns-per-year 2 --validate 1
   ```
   OR 
   ```powershell
     $ java -jar .\validator\validator_cli.jar .\out\data\2018_5f670_Patient.json -version 4.0.1 -ig .\validator\package_v8.0.1_R4
   ```
   A valid `.json` file is necessary to run the validator in command line directly as `java -jar ...`.  
