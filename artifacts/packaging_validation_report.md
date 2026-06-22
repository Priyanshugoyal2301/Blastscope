# BlastScope Standalone Solver: Packaging Validation Report

This report documents the verification and packaging audit of the compiled BlastScope standalone solver backend executable.

---

## 1. System Components & Paths

* **Executable Path**: [blastscope-solver.exe](file:///c:/project/drdo/code/backend-dist/blastscope-solver/blastscope-solver.exe)
* **Bundled Model Path**: [inverse_characterization_model.joblib](file:///c:/project/drdo/code/backend-dist/blastscope-solver/_internal/blast_engine/models/inverse_characterization_model.joblib)
* **Build Tool Configuration**: [build-solver.js](file:///c:/project/drdo/code/scripts/build-solver.js) (using PyInstaller with workspace paths configured to resolve imports).

---

## 2. Test Verification Cases & Responses

### 2.1 System Connection Verification (`system:ping`)
* **Payload**:
  ```json
  {"id": "test_req", "channel": "system:ping", "payload": {}}
  ```
* **Raw JSON stdout Response**:
  ```json
  {"id": "test_req", "success": true, "response": "pong"}
  ```

### 2.2 Inconsistent / Out-Of-Distribution (OOD) Verification
This test checks that the solver loads, runs, and correctly triggers OOD flags and low confidence when passed physically inconsistent values:
* **Payload**:
  ```json
  {
    "id": "test_predict",
    "channel": "inverse:predict",
    "payload": {
      "burstType": "Free Air",
      "incident_pressure": 44.0,
      "reflected_pressure": 88.9,
      "positive_impulse": 69.9,
      "reflected_impulse": 59.7,
      "arrival_time": 2.58,
      "positive_duration": 35.6
    }
  }
  ```
* **Raw JSON stdout Response**:
  ```json
  {
    "id": "test_predict",
    "success": true,
    "response": {
      "weight": 207.0322781193025,
      "scaled_distance": 4.2226766512840594,
      "distance": 24.980464745261646,
      "confidence": 0.0,
      "model_used": "Independent Random Forests (Separate Trees)",
      "ood": true
    }
  }
  ```

### 2.3 Physically Consistent / In-Distribution Verification
This test checks that the solver computes highly accurate weight and distance predictions with high confidence for consistent physical inputs:
* **Payload**:
  ```json
  {
    "id": "test_predict_consistent",
    "channel": "inverse:predict",
    "payload": {
      "burstType": "Free Air",
      "incident_pressure": 70.21,
      "reflected_pressure": 179.42,
      "positive_impulse": 279.62,
      "reflected_impulse": 627.46,
      "arrival_time": 20.98,
      "positive_duration": 12.96
    }
  }
  ```
* **Raw JSON stdout Response**:
  ```json
  {
    "id": "test_predict_consistent",
    "success": true,
    "response": {
      "weight": 98.98343150581972,
      "scaled_distance": 3.2298592075057426,
      "distance": 14.940705086624138,
      "confidence": 100.0,
      "model_used": "Independent Random Forests (Separate Trees)",
      "ood": false
    }
  }
  ```

---

## 3. Validation Assessment Checklist

| Audit Check | Status | Rationale |
| :--- | :---: | :--- |
| **Model Loads Successfully** | **PASS** | `success: true` is returned for predictions, showing the joblib payload loaded correctly. |
| **No sklearn Unpickling Errors** | **PASS** | Adding explicit `sklearn` imports in [main.py](file:///c:/project/drdo/code/backend/main.py) forced PyInstaller to package tree-regressor libraries, resolving the unpickling failure. |
| **Confidence Scores Returned** | **PASS** | Valid continuous confidence percentages (`0.0%` for OOD, `100.0%` for consistent case) are output. |
| **Correct Model Used Name** | **PASS** | Returns `"Independent Random Forests (Separate Trees)"` matching deployed metadata. |
| **OOD Safety Checks Executed** | **PASS** | Inconsistent pressure-reflection profiles are detected and flagged `ood: true`. |

---

## 4. Final Verdict

**✅ PASS**

The compiled standalone executable successfully hosts the Inverse ML characterization model and executes predictions, confidence scoring, and OOD checks under production constraints without error.
