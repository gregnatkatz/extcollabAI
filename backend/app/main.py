from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.config import settings
from app.auth import get_current_user, get_current_user_optional, require_pi, User
from app.audit import audit_logger, audit_middleware

app = FastAPI(
    title="ContosoHealth Research Platform API",
    description="Secure research platform with Entra ID authentication and RBAC",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.is_production() else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.middleware("http")(audit_middleware)

class UserProfile(BaseModel):
    userId: str
    email: str
    name: str
    institution: str
    accountType: str
    accessExpires: str
    projects: List[str]

class Project(BaseModel):
    projectId: str
    name: str
    piName: str
    piEmail: str
    fabricWorkspaceUrl: Optional[str]
    mlWorkspaceUrl: Optional[str]
    status: str
    createdAt: str
    description: str

class Notebook(BaseModel):
    notebookId: str
    name: str
    language: str
    author: str
    modified: str
    status: str
    fabricUrl: str

class Dataset(BaseModel):
    datasetId: str
    name: str
    rows: int
    size: str
    tables: int
    security: str
    accessLevel: str

class Model(BaseModel):
    modelId: str
    name: str
    version: str
    framework: str
    status: str
    gpus: int
    latency: str
    accuracy: float
    mlStudioUrl: str

class ExportRequest(BaseModel):
    requestId: str
    requestNumber: str
    projectId: str
    requestorEmail: str
    datasetName: str
    rowCount: Optional[int]
    justification: str
    status: str
    piReviewerEmail: str
    requestedAt: str
    reviewedAt: Optional[str]
    reviewNotes: Optional[str]
    downloadUrl: Optional[str]
    downloadExpiresAt: Optional[str]

class CreateExportRequest(BaseModel):
    projectId: str
    datasetName: str
    rowCount: Optional[int]
    justification: str

class ReviewExportRequest(BaseModel):
    decision: str
    notes: str

class Notification(BaseModel):
    notificationId: str
    userId: str
    type: str
    message: str
    isRead: bool
    relatedEntityType: Optional[str]
    relatedEntityId: Optional[str]
    createdAt: str

class Activity(BaseModel):
    activityId: str
    activityType: str
    user: str
    timestamp: str
    details: str

class AccessRequest(BaseModel):
    fullName: str
    email: str
    institution: str
    position: str
    projectInterest: str
    researchPurpose: str
    dataNeeded: str
    hipaaTraining: bool
    irbApproval: bool
    dataSecurityAgreement: bool
    noExternalSharing: bool
    institutionalAgreement: bool

mock_user = {
    "userId": "user-001",
    "email": "dr.smith@contosohealth.com",
    "name": "Dr. Sarah Smith",
    "institution": "ContosoHealth Orlando",
    "accountType": "Staff",
    "accessExpires": (datetime.now() + timedelta(days=365)).isoformat(),
    "projects": ["proj-001", "proj-002", "proj-004"]
}

mock_projects = [
    {
        "projectId": "proj-001",
        "name": "Cardiac Arrhythmia Prediction Study",
        "piName": "Dr. Sarah Smith",
        "piEmail": "dr.smith@contosohealth.com",
        "fabricWorkspaceUrl": "https://fabric.microsoft.com/workspace/cardiac-arrhythmia",
        "mlWorkspaceUrl": "https://ml.azure.com/workspace/cardiac-ml",
        "status": "Active",
        "createdAt": "2024-01-15T10:00:00Z",
        "description": "Machine learning models to predict atrial fibrillation using ECG data and patient history"
    },
    {
        "projectId": "proj-002",
        "name": "Heart Failure Readmission Analysis",
        "piName": "Dr. Sarah Smith",
        "piEmail": "dr.smith@contosohealth.com",
        "fabricWorkspaceUrl": "https://fabric.microsoft.com/workspace/heart-failure",
        "mlWorkspaceUrl": "https://ml.azure.com/workspace/hf-ml",
        "status": "Active",
        "createdAt": "2024-02-20T14:30:00Z",
        "description": "Analyzing factors contributing to 30-day readmission rates in heart failure patients"
    },
    {
        "projectId": "proj-003",
        "name": "Coronary Artery Disease Risk Modeling",
        "piName": "Dr. Michael Chen",
        "piEmail": "dr.chen@contosohealth.com",
        "fabricWorkspaceUrl": "https://fabric.microsoft.com/workspace/cad-risk",
        "mlWorkspaceUrl": "https://ml.azure.com/workspace/cad-ml",
        "status": "Active",
        "createdAt": "2024-03-10T09:15:00Z",
        "description": "Deep learning models for early detection of coronary artery disease using imaging and biomarkers"
    },
    {
        "projectId": "proj-004",
        "name": "Real-Time ECG Inference on H100",
        "piName": "Dr. Sarah Smith",
        "piEmail": "dr.smith@contosohealth.com",
        "fabricWorkspaceUrl": "https://fabric.microsoft.com/workspace/ecg-inference",
        "mlWorkspaceUrl": "https://ml.azure.com/workspace/ecg-inference-ml",
        "status": "Active",
        "createdAt": "2024-10-01T08:00:00Z",
        "description": "Production inference pipeline for real-time arrhythmia detection using H100 GPUs with sub-50ms latency"
    }
]

mock_notebooks = {
    "proj-001": [
        {
            "notebookId": "nb-001",
            "name": "ECG Signal Processing Pipeline",
            "language": "Python",
            "author": "Dr. Sarah Smith",
            "modified": "2024-10-15T16:45:00Z",
            "status": "Ready",
            "fabricUrl": "https://fabric.microsoft.com/notebook/ecg-processing"
        },
        {
            "notebookId": "nb-002",
            "name": "Arrhythmia Classification Model",
            "language": "Python",
            "author": "Dr. Sarah Smith",
            "modified": "2024-10-18T11:20:00Z",
            "status": "Running",
            "fabricUrl": "https://fabric.microsoft.com/notebook/arrhythmia-model"
        },
        {
            "notebookId": "nb-003",
            "name": "Feature Engineering - Heart Rate Variability",
            "language": "Python",
            "author": "Research Assistant",
            "modified": "2024-10-12T09:30:00Z",
            "status": "Ready",
            "fabricUrl": "https://fabric.microsoft.com/notebook/hrv-features"
        }
    ],
    "proj-002": [
        {
            "notebookId": "nb-004",
            "name": "Readmission Risk Factors Analysis",
            "language": "Python",
            "author": "Dr. Sarah Smith",
            "modified": "2024-10-17T14:00:00Z",
            "status": "Ready",
            "fabricUrl": "https://fabric.microsoft.com/notebook/readmission-analysis"
        },
        {
            "notebookId": "nb-005",
            "name": "Patient Cohort Selection",
            "language": "SQL",
            "author": "Data Analyst",
            "modified": "2024-10-10T10:15:00Z",
            "status": "Ready",
            "fabricUrl": "https://fabric.microsoft.com/notebook/cohort-selection"
        }
    ],
    "proj-004": [
        {
            "notebookId": "nb-006",
            "name": "Real-Time Inference Pipeline",
            "language": "Python",
            "author": "Dr. Sarah Smith",
            "modified": "2024-10-19T10:00:00Z",
            "status": "Ready",
            "fabricUrl": "https://fabric.microsoft.com/notebook/inference-pipeline",
            "executableCode": """import numpy as np
import time
from datetime import datetime

def preprocess_ecg(ecg_signal):
    normalized = (ecg_signal - np.mean(ecg_signal)) / np.std(ecg_signal)
    filtered = normalized * 0.95
    return filtered

def run_inference_on_h100(preprocessed_data, model_name="AFib Detection LSTM v2.3"):
    start_time = time.time()
    
    predictions = {
        "normal_sinus_rhythm": 0.12,
        "atrial_fibrillation": 0.78,
        "premature_ventricular_contraction": 0.06,
        "ventricular_tachycardia": 0.04
    }
    
    inference_time_ms = (time.time() - start_time) * 1000
    
    return {
        "model": model_name,
        "predictions": predictions,
        "predicted_class": "atrial_fibrillation",
        "confidence": 0.78,
        "inference_time_ms": round(inference_time_ms + 42, 2),  # Simulate 42ms on H100
        "gpu_used": "H100-0",
        "timestamp": datetime.now().isoformat()
    }

print("=== Real-Time ECG Inference on H100 GPU ===\\n")

ecg_signal = np.random.randn(5000) * 0.5 + np.sin(np.linspace(0, 20*np.pi, 5000))
print(f"Input: ECG signal with {len(ecg_signal)} samples")

preprocessed = preprocess_ecg(ecg_signal)
print(f"Preprocessing: Complete (normalized and filtered)\\n")

result = run_inference_on_h100(preprocessed)

print(f"Model: {result['model']}")
print(f"GPU: {result['gpu_used']}")
print(f"Inference Time: {result['inference_time_ms']}ms\\n")

print("Predictions:")
for condition, prob in result['predictions'].items():
    bar = '█' * int(prob * 50)
    print(f"  {condition:40s} {prob:.2%} {bar}")

print(f"\\n✓ Predicted: {result['predicted_class'].upper()} (confidence: {result['confidence']:.1%})")
print(f"✓ Latency: {result['inference_time_ms']}ms (target: <50ms)")
"""
        },
        {
            "notebookId": "nb-007",
            "name": "Statistical Analysis - Heart Rate Variability",
            "language": "R",
            "author": "Dr. Sarah Smith",
            "modified": "2024-10-18T14:30:00Z",
            "status": "Ready",
            "fabricUrl": "https://fabric.microsoft.com/notebook/hrv-stats-r",
            "executableCode": """# Heart Rate Variability Statistical Analysis

library(ggplot2)

set.seed(42)
n_patients <- 1000

hrv_data <- data.frame(
  patient_id = 1:n_patients,
  rmssd = rnorm(n_patients, mean = 42, sd = 15),
  sdnn = rnorm(n_patients, mean = 50, sd = 18),
  pnn50 = rnorm(n_patients, mean = 25, sd = 12),
  lf_hf_ratio = rnorm(n_patients, mean = 1.5, sd = 0.8),
  age = sample(45:85, n_patients, replace = TRUE),
  has_afib = sample(c(0, 1), n_patients, replace = TRUE, prob = c(0.7, 0.3))
)

cat("=== Heart Rate Variability Analysis ===\\n\\n")
cat(sprintf("Dataset: %d patients with ECG-derived HRV metrics\\n\\n", n_patients))

cat("Summary Statistics:\\n")
cat(sprintf("  RMSSD (ms):     Mean = %.2f, SD = %.2f\\n", 
            mean(hrv_data$rmssd), sd(hrv_data$rmssd)))
cat(sprintf("  SDNN (ms):      Mean = %.2f, SD = %.2f\\n", 
            mean(hrv_data$sdnn), sd(hrv_data$sdnn)))
cat(sprintf("  pNN50 (%%):      Mean = %.2f, SD = %.2f\\n", 
            mean(hrv_data$pnn50), sd(hrv_data$pnn50)))
cat(sprintf("  LF/HF Ratio:    Mean = %.2f, SD = %.2f\\n\\n", 
            mean(hrv_data$lf_hf_ratio), sd(hrv_data$lf_hf_ratio)))

cat("Correlation with AFib Status:\\n")
cor_rmssd <- cor(hrv_data$rmssd, hrv_data$has_afib)
cor_sdnn <- cor(hrv_data$sdnn, hrv_data$has_afib)
cor_pnn50 <- cor(hrv_data$pnn50, hrv_data$has_afib)
cor_lf_hf <- cor(hrv_data$lf_hf_ratio, hrv_data$has_afib)

cat(sprintf("  RMSSD:     r = %.3f\\n", cor_rmssd))
cat(sprintf("  SDNN:      r = %.3f\\n", cor_sdnn))
cat(sprintf("  pNN50:     r = %.3f\\n", cor_pnn50))
cat(sprintf("  LF/HF:     r = %.3f\\n\\n", cor_lf_hf))

afib_rmssd <- hrv_data$rmssd[hrv_data$has_afib == 1]
no_afib_rmssd <- hrv_data$rmssd[hrv_data$has_afib == 0]
t_result <- t.test(afib_rmssd, no_afib_rmssd)

cat("T-Test: RMSSD in AFib vs No AFib\\n")
cat(sprintf("  AFib Mean:     %.2f ms\\n", mean(afib_rmssd)))
cat(sprintf("  No AFib Mean:  %.2f ms\\n", mean(no_afib_rmssd)))
cat(sprintf("  t-statistic:   %.3f\\n", t_result$statistic))
cat(sprintf("  p-value:       %.4f\\n\\n", t_result$p.value))

model <- glm(has_afib ~ rmssd + sdnn + pnn50 + lf_hf_ratio + age, 
             data = hrv_data, family = binomial)

cat("Logistic Regression Model (AFib Prediction):\\n")
cat(sprintf("  AIC: %.2f\\n", AIC(model)))
cat(sprintf("  Null Deviance: %.2f\\n", model$null.deviance))
cat(sprintf("  Residual Deviance: %.2f\\n\\n", model$deviance))

cat("✓ Analysis Complete\\n")
cat("✓ Results ready for export (summary statistics, correlations, model coefficients)\\n")
"""
        },
        {
            "notebookId": "nb-008",
            "name": "Spark Streaming - ECG Data Pipeline",
            "language": "Scala",
            "author": "Data Engineering Team",
            "modified": "2024-10-17T09:15:00Z",
            "status": "Ready",
            "fabricUrl": "https://fabric.microsoft.com/notebook/ecg-spark-scala",
            "executableCode": """// ECG Data Streaming Pipeline with Apache Spark
// Processing real-time ECG signals for arrhythmia detection

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val spark = SparkSession.builder()
  .appName("ECG Streaming Pipeline")
  .getOrCreate()

import spark.implicits._

println("=== ECG Data Streaming Pipeline ===\\n")

val ecgSchema = StructType(Seq(
  StructField("patient_id", StringType, false),
  StructField("timestamp", TimestampType, false),
  StructField("heart_rate", IntegerType, false),
  StructField("rr_interval", DoubleType, false),
  StructField("qrs_duration", DoubleType, false),
  StructField("qt_interval", DoubleType, false),
  StructField("signal_quality", DoubleType, false)
))

val mockEcgData = Seq(
  ("P001", "2024-10-19 10:00:00", 72, 833.0, 95.0, 380.0, 0.98),
  ("P002", "2024-10-19 10:00:01", 145, 414.0, 110.0, 420.0, 0.85),
  ("P003", "2024-10-19 10:00:02", 68, 882.0, 92.0, 375.0, 0.99),
  ("P004", "2024-10-19 10:00:03", 158, 380.0, 115.0, 450.0, 0.82),
  ("P005", "2024-10-19 10:00:04", 75, 800.0, 98.0, 390.0, 0.97)
).toDF("patient_id", "timestamp_str", "heart_rate", "rr_interval", 
       "qrs_duration", "qt_interval", "signal_quality")
  .withColumn("timestamp", to_timestamp($"timestamp_str"))
  .drop("timestamp_str")

println(s"Ingested ${mockEcgData.count()} ECG records\\n")

val processedData = mockEcgData
  .withColumn("hr_category", 
    when($"heart_rate" < 60, "Bradycardia")
    .when($"heart_rate" > 100, "Tachycardia")
    .otherwise("Normal"))
  .withColumn("qt_corrected", $"qt_interval" / sqrt($"rr_interval" / 1000.0))
  .withColumn("arrhythmia_risk", 
    when($"hr_category" =!= "Normal" && $"qt_corrected" > 440, "High")
    .when($"hr_category" =!= "Normal" || $"qt_corrected" > 440, "Medium")
    .otherwise("Low"))

println("Processing Statistics:")
println(s"  Total Records: ${processedData.count()}")
println(s"  Avg Heart Rate: ${processedData.agg(avg("heart_rate")).first().getDouble(0).formatted("%.1f")} bpm")
println(s"  Avg QTc: ${processedData.agg(avg("qt_corrected")).first().getDouble(0).formatted("%.1f")} ms\\n")

println("Heart Rate Distribution:")
processedData.groupBy("hr_category").count().orderBy("hr_category").collect().foreach { row =>
  println(s"  ${row.getString(0)}: ${row.getLong(1)} patients")
}

println("\\nArrhythmia Risk Distribution:")
processedData.groupBy("arrhythmia_risk").count().orderBy("arrhythmia_risk").collect().foreach { row =>
  println(s"  ${row.getString(0)} Risk: ${row.getLong(1)} patients")
}

val highRiskPatients = processedData.filter($"arrhythmia_risk" === "High")
println(s"\\nHigh Risk Patients: ${highRiskPatients.count()}")
if (highRiskPatients.count() > 0) {
  println("  Patient IDs: " + highRiskPatients.select("patient_id").collect().map(_.getString(0)).mkString(", "))
}

println("\\n✓ Pipeline Complete")
println("✓ Results ready for export (aggregated metrics, risk scores, patient summaries)")
"""
        }
    ]
}

mock_datasets = {
    "proj-001": [
        {
            "datasetId": "ds-001",
            "name": "ECG Recordings Database",
            "rows": 125000,
            "size": "45.2 GB",
            "tables": 3,
            "security": "PHI Protected",
            "accessLevel": "Contributor"
        },
        {
            "datasetId": "ds-002",
            "name": "Patient Demographics & History",
            "rows": 8500,
            "size": "2.1 GB",
            "tables": 5,
            "security": "PHI Protected",
            "accessLevel": "Contributor"
        },
        {
            "datasetId": "ds-003",
            "name": "Arrhythmia Event Labels",
            "rows": 15200,
            "size": "850 MB",
            "tables": 2,
            "security": "PHI Protected",
            "accessLevel": "Viewer"
        }
    ],
    "proj-002": [
        {
            "datasetId": "ds-004",
            "name": "Heart Failure Admissions",
            "rows": 3200,
            "size": "1.8 GB",
            "tables": 4,
            "security": "PHI Protected",
            "accessLevel": "Contributor"
        },
        {
            "datasetId": "ds-005",
            "name": "Medication History",
            "rows": 45000,
            "size": "3.5 GB",
            "tables": 2,
            "security": "PHI Protected",
            "accessLevel": "Contributor"
        }
    ],
    "proj-004": [
        {
            "datasetId": "ds-006",
            "name": "Real-Time ECG Stream",
            "rows": 2500000,
            "size": "180 GB",
            "tables": 1,
            "security": "PHI Protected",
            "accessLevel": "Contributor"
        },
        {
            "datasetId": "ds-007",
            "name": "Inference Results Archive",
            "rows": 8500000,
            "size": "95 GB",
            "tables": 2,
            "security": "PHI Protected",
            "accessLevel": "Viewer"
        }
    ]
}

mock_models = {
    "proj-001": [
        {
            "modelId": "model-001",
            "name": "AFib Detection LSTM",
            "version": "v2.3",
            "framework": "PyTorch",
            "status": "Deployed",
            "gpus": 2,
            "latency": "45ms",
            "accuracy": 0.94,
            "mlStudioUrl": "https://ml.azure.com/model/afib-lstm"
        },
        {
            "modelId": "model-002",
            "name": "Multi-Class Arrhythmia CNN",
            "version": "v1.8",
            "framework": "TensorFlow",
            "status": "Training",
            "gpus": 4,
            "latency": "N/A",
            "accuracy": 0.89,
            "mlStudioUrl": "https://ml.azure.com/model/arrhythmia-cnn"
        }
    ],
    "proj-002": [
        {
            "modelId": "model-003",
            "name": "Readmission Risk XGBoost",
            "version": "v3.1",
            "framework": "XGBoost",
            "status": "Deployed",
            "gpus": 1,
            "latency": "12ms",
            "accuracy": 0.87,
            "mlStudioUrl": "https://ml.azure.com/model/readmission-xgb"
        }
    ],
    "proj-004": [
        {
            "modelId": "model-004",
            "name": "Production AFib Detector",
            "version": "v3.0",
            "framework": "PyTorch",
            "status": "Deployed",
            "gpus": 4,
            "latency": "42ms",
            "accuracy": 0.96,
            "mlStudioUrl": "https://ml.azure.com/model/production-afib"
        }
    ]
}

mock_export_requests = [
    {
        "requestId": "exp-001",
        "requestNumber": "EXP-2024-001",
        "projectId": "proj-001",
        "requestorEmail": "researcher@external.edu",
        "datasetName": "ECG Recordings Database",
        "rowCount": 1000,
        "justification": "Need sample data for validation of external arrhythmia detection algorithm",
        "status": "Pending",
        "piReviewerEmail": "dr.smith@contosohealth.com",
        "requestedAt": "2024-10-18T09:30:00Z",
        "reviewedAt": None,
        "reviewNotes": None,
        "downloadUrl": None,
        "downloadExpiresAt": None
    },
    {
        "requestId": "exp-002",
        "requestNumber": "EXP-2024-002",
        "projectId": "proj-002",
        "requestorEmail": "dr.smith@contosohealth.com",
        "datasetName": "Heart Failure Admissions",
        "rowCount": 500,
        "justification": "Export for presentation at American Heart Association conference",
        "status": "Approved",
        "piReviewerEmail": "dr.smith@contosohealth.com",
        "requestedAt": "2024-10-15T14:20:00Z",
        "reviewedAt": "2024-10-16T10:15:00Z",
        "reviewNotes": "Approved for conference presentation. Ensure all PHI is removed.",
        "downloadUrl": "https://storage.azure.com/exports/exp-2024-002.zip?sas=token",
        "downloadExpiresAt": (datetime.now() + timedelta(hours=24)).isoformat()
    }
]

mock_notifications = [
    {
        "notificationId": "notif-001",
        "userId": "user-001",
        "type": "Info",
        "message": "Your export request EXP-2024-002 has been approved",
        "isRead": False,
        "relatedEntityType": "Export",
        "relatedEntityId": "exp-002",
        "createdAt": "2024-10-16T10:15:00Z"
    },
    {
        "notificationId": "notif-002",
        "userId": "user-001",
        "type": "Success",
        "message": "Model 'AFib Detection LSTM' training completed successfully",
        "isRead": False,
        "relatedEntityType": "Model",
        "relatedEntityId": "model-001",
        "createdAt": "2024-10-17T16:45:00Z"
    },
    {
        "notificationId": "notif-003",
        "userId": "user-001",
        "type": "Warning",
        "message": "Your access to project 'Cardiac Arrhythmia Prediction Study' expires in 30 days",
        "isRead": True,
        "relatedEntityType": "Project",
        "relatedEntityId": "proj-001",
        "createdAt": "2024-10-10T08:00:00Z"
    }
]

mock_activities = {
    "proj-001": [
        {
            "activityId": "act-001",
            "activityType": "NotebookOpened",
            "user": "Dr. Sarah Smith",
            "timestamp": "2024-10-18T11:20:00Z",
            "details": "Opened notebook 'Arrhythmia Classification Model'"
        },
        {
            "activityId": "act-002",
            "activityType": "ModelTrained",
            "user": "Dr. Sarah Smith",
            "timestamp": "2024-10-17T16:45:00Z",
            "details": "Completed training for 'AFib Detection LSTM v2.3'"
        },
        {
            "activityId": "act-003",
            "activityType": "DatasetAccessed",
            "user": "Research Assistant",
            "timestamp": "2024-10-17T14:30:00Z",
            "details": "Accessed 'ECG Recordings Database' for analysis"
        },
        {
            "activityId": "act-004",
            "activityType": "ExportRequested",
            "user": "researcher@external.edu",
            "timestamp": "2024-10-18T09:30:00Z",
            "details": "Requested export of 1000 rows from 'ECG Recordings Database'"
        }
    ],
    "proj-002": [
        {
            "activityId": "act-005",
            "activityType": "NotebookOpened",
            "user": "Dr. Sarah Smith",
            "timestamp": "2024-10-17T14:00:00Z",
            "details": "Opened notebook 'Readmission Risk Factors Analysis'"
        },
        {
            "activityId": "act-006",
            "activityType": "ExportApproved",
            "user": "Dr. Sarah Smith",
            "timestamp": "2024-10-16T10:15:00Z",
            "details": "Approved export request EXP-2024-002"
        }
    ]
}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/v1/user/profile")
async def get_user_profile(user: User = Depends(get_current_user)):
    """Get current user profile from Entra ID token"""
    return {
        "userId": user.user_id,
        "email": user.email,
        "name": user.name,
        "institution": user.institution,
        "accountType": "Staff" if not user.email.endswith("@external.edu") else "Guest",
        "accessExpires": (datetime.now() + timedelta(days=180)).isoformat(),
        "projects": mock_user["projects"],
        "roles": user.roles
    }

@app.get("/api/v1/user/projects")
async def get_user_projects():
    user_project_ids = mock_user["projects"]
    user_projects = [p for p in mock_projects if p["projectId"] in user_project_ids]
    
    for project in user_projects:
        project_id = project["projectId"]
        project["stats"] = {
            "notebooks": len(mock_notebooks.get(project_id, [])),
            "datasets": len(mock_datasets.get(project_id, [])),
            "models": len(mock_models.get(project_id, [])),
            "recentActivity": len(mock_activities.get(project_id, []))
        }
    
    return user_projects

@app.get("/api/v1/projects/{project_id}")
async def get_project_details(project_id: str):
    project = next((p for p in mock_projects if p["projectId"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        **project,
        "notebooks": mock_notebooks.get(project_id, []),
        "datasets": mock_datasets.get(project_id, []),
        "models": mock_models.get(project_id, [])
    }

@app.get("/api/v1/projects/{project_id}/activity")
async def get_project_activity(project_id: str, limit: int = 20):
    activities = mock_activities.get(project_id, [])
    return activities[:limit]

@app.get("/api/v1/projects/{project_id}/notebooks")
async def get_project_notebooks(project_id: str):
    return mock_notebooks.get(project_id, [])

@app.get("/api/v1/projects/{project_id}/datasets")
async def get_project_datasets(project_id: str):
    return mock_datasets.get(project_id, [])

@app.get("/api/v1/projects/{project_id}/models")
async def get_project_models(project_id: str):
    return mock_models.get(project_id, [])

@app.get("/api/v1/exports/my-requests")
async def get_my_export_requests(status: Optional[str] = None):
    requests = mock_export_requests
    if status:
        requests = [r for r in requests if r["status"] == status]
    return requests

@app.post("/api/v1/exports/request")
async def create_export_request(request: CreateExportRequest):
    new_request = {
        "requestId": f"exp-{str(uuid.uuid4())[:8]}",
        "requestNumber": f"EXP-2024-{len(mock_export_requests) + 1:03d}",
        "projectId": request.projectId,
        "requestorEmail": mock_user["email"],
        "datasetName": request.datasetName,
        "rowCount": request.rowCount,
        "justification": request.justification,
        "status": "Pending",
        "piReviewerEmail": "dr.smith@contosohealth.com",
        "requestedAt": datetime.now().isoformat(),
        "reviewedAt": None,
        "reviewNotes": None,
        "downloadUrl": None,
        "downloadExpiresAt": None
    }
    mock_export_requests.append(new_request)
    return {
        "requestId": new_request["requestId"],
        "requestNumber": new_request["requestNumber"],
        "status": "Pending",
        "estimatedApprovalTime": "24-48 hours"
    }

@app.post("/api/v1/exports/{request_id}/review")
async def review_export_request(
    request_id: str, 
    review: ReviewExportRequest,
    user: User = Depends(require_pi())
):
    """Review export request - PI only"""
    request = next((r for r in mock_export_requests if r["requestId"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Export request not found")
    
    request["status"] = review.decision
    request["reviewedAt"] = datetime.now().isoformat()
    request["reviewNotes"] = review.notes
    request["reviewedBy"] = user.email
    
    if review.decision == "Approved":
        request["downloadUrl"] = f"https://storage.azure.com/exports/{request['requestNumber']}.zip?sas=token"
        request["downloadExpiresAt"] = (datetime.now() + timedelta(hours=24)).isoformat()
    
    await audit_logger.log_request(
        request=Request,
        user_id=user.user_id,
        user_email=user.email,
        activity_type="ExportReviewed",
        resource_id=request_id,
        activity_details={"decision": review.decision, "notes": review.notes}
    )
    
    return request

@app.get("/api/v1/notifications")
async def get_notifications(unreadOnly: bool = False):
    notifications = mock_notifications
    if unreadOnly:
        notifications = [n for n in notifications if not n["isRead"]]
    return notifications

@app.patch("/api/v1/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    notification = next((n for n in mock_notifications if n["notificationId"] == notification_id), None)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification["isRead"] = True
    return {"success": True}

@app.post("/api/v1/access-requests")
async def create_access_request(request: AccessRequest):
    """Submit external researcher access request"""
    
    request_id = str(uuid.uuid4())
    
    return {
        "requestId": request_id,
        "status": "Pending",
        "message": "Access request submitted successfully. A PI will review within 3-5 business days.",
        "estimatedReviewDate": (datetime.now() + timedelta(days=3)).isoformat()
    }

@app.get("/api/v1/compute/h100")
async def get_h100_status():
    return {
        "totalGPUs": 8,
        "availableGPUs": 4,
        "activeJobs": [
            {
                "jobId": "job-001",
                "projectName": "Cardiac Arrhythmia Prediction Study",
                "modelName": "Multi-Class Arrhythmia CNN",
                "gpusUsed": 4,
                "status": "Training",
                "progress": 67
            }
        ]
    }

@app.post("/api/v1/auth/login")
async def entra_id_login(email: str, password: str):
    return {
        "accessToken": f"mock_token_{uuid.uuid4()}",
        "refreshToken": f"mock_refresh_{uuid.uuid4()}",
        "expiresIn": 3600,
        "tokenType": "Bearer",
        "user": mock_user
    }

@app.post("/api/v1/auth/refresh")
async def refresh_token(refreshToken: str):
    return {
        "accessToken": f"mock_token_{uuid.uuid4()}",
        "expiresIn": 3600
    }

@app.get("/api/v1/auth/validate")
async def validate_token():
    return {
        "valid": True,
        "user": mock_user
    }

@app.get("/api/v1/policies")
async def get_policies():
    return [
        {
            "policyId": "pol-001",
            "name": "PHI Data Access Policy",
            "type": "DataAccess",
            "description": "Controls access to PHI-protected datasets",
            "status": "Active",
            "rules": [
                {"condition": "role == 'PI'", "action": "allow", "resources": ["all_datasets"]},
                {"condition": "role == 'Contributor'", "action": "allow", "resources": ["assigned_datasets"]},
                {"condition": "role == 'Viewer'", "action": "read_only", "resources": ["assigned_datasets"]}
            ],
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-10-01T00:00:00Z"
        },
        {
            "policyId": "pol-002",
            "name": "Export Approval Policy",
            "type": "ExportControl",
            "description": "Requires PI approval for all data exports",
            "status": "Active",
            "rules": [
                {"condition": "export_requested", "action": "require_pi_approval", "timeout": "48h"}
            ],
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-09-15T00:00:00Z"
        },
        {
            "policyId": "pol-003",
            "name": "Model Deployment Policy",
            "type": "MLOps",
            "description": "Requires validation before production deployment",
            "status": "Active",
            "rules": [
                {"condition": "accuracy < 0.85", "action": "block_deployment"},
                {"condition": "no_bias_check", "action": "require_review"}
            ],
            "createdAt": "2024-02-01T00:00:00Z",
            "updatedAt": "2024-10-10T00:00:00Z"
        }
    ]

@app.get("/api/v1/policies/{policy_id}")
async def get_policy_details(policy_id: str):
    policies = await get_policies()
    policy = next((p for p in policies if p["policyId"] == policy_id), None)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@app.get("/api/v1/fabric/workspaces")
async def get_fabric_workspaces():
    return [
        {
            "workspaceId": "ws-001",
            "name": "Cardiac Research Workspace",
            "description": "Primary workspace for cardiac arrhythmia studies",
            "capacityId": "cap-f64-001",
            "region": "East US",
            "status": "Active",
            "owner": "dr.smith@contosohealth.com",
            "members": 5,
            "storageUsed": "2.3 TB",
            "storageLimit": "10 TB",
            "createdAt": "2024-01-15T10:00:00Z",
            "lastAccessed": "2024-10-19T14:30:00Z"
        },
        {
            "workspaceId": "ws-002",
            "name": "Heart Failure Analytics",
            "description": "Workspace for heart failure readmission analysis",
            "capacityId": "cap-f64-001",
            "region": "East US",
            "status": "Active",
            "owner": "dr.smith@contosohealth.com",
            "members": 3,
            "storageUsed": "1.8 TB",
            "storageLimit": "10 TB",
            "createdAt": "2024-02-20T14:30:00Z",
            "lastAccessed": "2024-10-19T11:15:00Z"
        }
    ]

@app.get("/api/v1/fabric/workspaces/{workspace_id}")
async def get_fabric_workspace_details(workspace_id: str):
    workspaces = await get_fabric_workspaces()
    workspace = next((w for w in workspaces if w["workspaceId"] == workspace_id), None)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    workspace["items"] = {
        "notebooks": 8,
        "lakehouses": 3,
        "dataflows": 5,
        "semanticModels": 4,
        "reports": 12
    }
    workspace["compute"] = {
        "sparkPools": 2,
        "activeJobs": 1,
        "queuedJobs": 0
    }
    return workspace

@app.get("/api/v1/fabric/workspaces/{workspace_id}/lakehouses")
async def get_fabric_lakehouses(workspace_id: str):
    return [
        {
            "lakehouseId": "lh-001",
            "name": "ECG Data Lakehouse",
            "workspaceId": workspace_id,
            "storageUsed": "1.2 TB",
            "tables": 15,
            "files": 2500,
            "status": "Active",
            "createdAt": "2024-01-20T00:00:00Z"
        },
        {
            "lakehouseId": "lh-002",
            "name": "Patient Records Lakehouse",
            "workspaceId": workspace_id,
            "storageUsed": "800 GB",
            "tables": 22,
            "files": 1200,
            "status": "Active",
            "createdAt": "2024-02-01T00:00:00Z"
        }
    ]

@app.post("/api/v1/fabric/notebooks/{notebook_id}/execute")
async def execute_fabric_notebook(notebook_id: str):
    return {
        "executionId": f"exec-{uuid.uuid4()}",
        "notebookId": notebook_id,
        "status": "Running",
        "startedAt": datetime.now().isoformat(),
        "estimatedDuration": "5-10 minutes"
    }

@app.post("/api/v1/notebooks/{notebook_id}/run-inference")
async def run_inference_demo(notebook_id: str):
    """Execute inference notebook and return results"""
    import numpy as np
    import time
    
    start_time = time.time()
    
    ecg_signal = np.random.randn(5000) * 0.5 + np.sin(np.linspace(0, 20*np.pi, 5000))
    normalized = (ecg_signal - np.mean(ecg_signal)) / np.std(ecg_signal)
    
    predictions = {
        "normal_sinus_rhythm": 0.12,
        "atrial_fibrillation": 0.78,
        "premature_ventricular_contraction": 0.06,
        "ventricular_tachycardia": 0.04
    }
    
    inference_time = (time.time() - start_time) * 1000 + 42
    
    output_lines = [
        "=== Real-Time ECG Inference on H100 GPU ===",
        "",
        f"Input: ECG signal with {len(ecg_signal)} samples",
        "Preprocessing: Complete (normalized and filtered)",
        "",
        "Model: AFib Detection LSTM v2.3",
        "GPU: H100-0",
        f"Inference Time: {inference_time:.2f}ms",
        "",
        "Predictions:",
        f"  normal_sinus_rhythm                      12.00% {'█' * 6}",
        f"  atrial_fibrillation                      78.00% {'█' * 39}",
        f"  premature_ventricular_contraction         6.00% {'█' * 3}",
        f"  ventricular_tachycardia                   4.00% {'█' * 2}",
        "",
        "✓ Predicted: ATRIAL_FIBRILLATION (confidence: 78.0%)",
        f"✓ Latency: {inference_time:.2f}ms (target: <50ms)"
    ]
    
    return {
        "executionId": f"exec-{uuid.uuid4()}",
        "notebookId": notebook_id,
        "status": "Completed",
        "output": "\n".join(output_lines),
        "result": {
            "model": "AFib Detection LSTM v2.3",
            "predictions": predictions,
            "predicted_class": "atrial_fibrillation",
            "confidence": 0.78,
            "inference_time_ms": round(inference_time, 2),
            "gpu_used": "H100-0",
            "timestamp": datetime.now().isoformat()
        },
        "startedAt": datetime.now().isoformat(),
        "completedAt": datetime.now().isoformat(),
        "duration": f"{inference_time:.2f}ms"
    }

@app.post("/api/v1/notebooks/{notebook_id}/run-r")
async def run_r_notebook(notebook_id: str):
    """Execute R notebook and return results"""
    output_lines = [
        "=== Heart Rate Variability Analysis ===",
        "",
        "Dataset: 1000 patients with ECG-derived HRV metrics",
        "",
        "Summary Statistics:",
        "  RMSSD (ms):     Mean = 42.15, SD = 14.98",
        "  SDNN (ms):      Mean = 50.23, SD = 17.85",
        "  pNN50 (%):      Mean = 25.12, SD = 11.94",
        "  LF/HF Ratio:    Mean = 1.51, SD = 0.79",
        "",
        "Correlation with AFib Status:",
        "  RMSSD:     r = -0.042",
        "  SDNN:      r = -0.038",
        "  pNN50:     r = -0.051",
        "  LF/HF:     r = 0.028",
        "",
        "T-Test: RMSSD in AFib vs No AFib",
        "  AFib Mean:     41.85 ms",
        "  No AFib Mean:  42.28 ms",
        "  t-statistic:   -0.421",
        "  p-value:       0.6738",
        "",
        "Logistic Regression Model (AFib Prediction):",
        "  AIC: 1385.42",
        "  Null Deviance: 1383.89",
        "  Residual Deviance: 1375.42",
        "",
        "✓ Analysis Complete",
        "✓ Results ready for export (summary statistics, correlations, model coefficients)"
    ]
    
    return {
        "notebookId": notebook_id,
        "language": "R",
        "status": "completed",
        "output": "\n".join(output_lines),
        "result": {
            "summary_stats": {
                "rmssd_mean": 42.15,
                "sdnn_mean": 50.23,
                "pnn50_mean": 25.12,
                "lf_hf_ratio_mean": 1.51
            },
            "correlations": {
                "rmssd": -0.042,
                "sdnn": -0.038,
                "pnn50": -0.051,
                "lf_hf": 0.028
            },
            "model_aic": 1385.42
        },
        "executionTime": "2.3s",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/notebooks/{notebook_id}/run-scala")
async def run_scala_notebook(notebook_id: str):
    """Execute Scala/Spark notebook and return results"""
    output_lines = [
        "=== ECG Data Streaming Pipeline ===",
        "",
        "Ingested 5 ECG records",
        "",
        "Processing Statistics:",
        "  Total Records: 5",
        "  Avg Heart Rate: 103.6 bpm",
        "  Avg QTc: 437.2 ms",
        "",
        "Heart Rate Distribution:",
        "  Bradycardia: 1 patients",
        "  Normal: 1 patients",
        "  Tachycardia: 3 patients",
        "",
        "Arrhythmia Risk Distribution:",
        "  High Risk: 2 patients",
        "  Low Risk: 1 patients",
        "  Medium Risk: 2 patients",
        "",
        "High Risk Patients: 2",
        "  Patient IDs: P002, P004",
        "",
        "✓ Pipeline Complete",
        "✓ Results ready for export (aggregated metrics, risk scores, patient summaries)"
    ]
    
    return {
        "notebookId": notebook_id,
        "language": "Scala",
        "status": "completed",
        "output": "\n".join(output_lines),
        "result": {
            "total_records": 5,
            "avg_heart_rate": 103.6,
            "avg_qtc": 437.2,
            "hr_distribution": {
                "Bradycardia": 1,
                "Normal": 1,
                "Tachycardia": 3
            },
            "risk_distribution": {
                "High": 2,
                "Medium": 2,
                "Low": 1
            },
            "high_risk_patients": ["P002", "P004"]
        },
        "executionTime": "1.8s",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/mlstudio/workspaces")
async def get_ml_workspaces():
    return [
        {
            "workspaceId": "mlws-001",
            "name": "Cardiac ML Workspace",
            "subscriptionId": "sub-001",
            "resourceGroup": "rg-cardiac-research",
            "region": "East US",
            "status": "Active",
            "computeTargets": 3,
            "models": 8,
            "endpoints": 4,
            "createdAt": "2024-01-15T10:00:00Z"
        }
    ]

@app.get("/api/v1/mlstudio/compute")
async def get_ml_compute_targets():
    return [
        {
            "computeId": "compute-h100-001",
            "name": "H100-GPU-Cluster",
            "type": "AmlCompute",
            "vmSize": "Standard_NC96ads_A100_v4",
            "gpuType": "H100",
            "minNodes": 0,
            "maxNodes": 8,
            "currentNodes": 4,
            "idleNodes": 0,
            "status": "Running",
            "location": "East US"
        },
        {
            "computeId": "compute-cpu-001",
            "name": "CPU-Cluster",
            "type": "AmlCompute",
            "vmSize": "Standard_D16s_v3",
            "minNodes": 0,
            "maxNodes": 10,
            "currentNodes": 2,
            "idleNodes": 1,
            "status": "Running",
            "location": "East US"
        }
    ]

@app.post("/api/v1/mlstudio/compute/{compute_id}/scale")
async def scale_ml_compute(compute_id: str, targetNodes: int):
    return {
        "computeId": compute_id,
        "targetNodes": targetNodes,
        "status": "Scaling",
        "estimatedTime": "3-5 minutes"
    }

@app.get("/api/v1/mlstudio/endpoints")
async def get_ml_endpoints():
    return [
        {
            "endpointId": "ep-001",
            "name": "afib-detection-endpoint",
            "modelName": "AFib Detection LSTM",
            "modelVersion": "v2.3",
            "status": "Healthy",
            "computeType": "H100",
            "instanceCount": 2,
            "requestsPerMinute": 450,
            "avgLatency": "45ms",
            "errorRate": 0.002,
            "deployedAt": "2024-10-10T00:00:00Z",
            "scoringUri": "https://afib-detection.eastus.inference.ml.azure.com/score"
        },
        {
            "endpointId": "ep-002",
            "name": "readmission-risk-endpoint",
            "modelName": "Readmission Risk XGBoost",
            "modelVersion": "v3.1",
            "status": "Healthy",
            "computeType": "CPU",
            "instanceCount": 3,
            "requestsPerMinute": 1200,
            "avgLatency": "12ms",
            "errorRate": 0.001,
            "deployedAt": "2024-09-25T00:00:00Z",
            "scoringUri": "https://readmission-risk.eastus.inference.ml.azure.com/score"
        }
    ]

@app.post("/api/v1/mlstudio/endpoints/{endpoint_id}/invoke")
async def invoke_ml_endpoint(endpoint_id: str, data: dict):
    return {
        "endpointId": endpoint_id,
        "prediction": {
            "class": "AFib Detected",
            "confidence": 0.94,
            "probabilities": {
                "Normal": 0.06,
                "AFib": 0.94
            }
        },
        "latency": "43ms",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/foundry/projects")
async def get_foundry_projects():
    return [
        {
            "projectId": "foundry-001",
            "name": "Cardiac Research Foundation",
            "description": "Azure AI Foundry project for cardiac research models",
            "status": "Active",
            "models": 5,
            "datasets": 8,
            "experiments": 23,
            "createdAt": "2024-01-15T00:00:00Z"
        }
    ]

@app.get("/api/v1/foundry/models")
async def get_foundry_models():
    return [
        {
            "modelId": "fm-001",
            "name": "GPT-4o Fine-tuned for Medical Notes",
            "baseModel": "gpt-4o",
            "version": "v1.2",
            "status": "Deployed",
            "accuracy": 0.92,
            "trainingDataset": "Medical Notes Corpus",
            "trainingDate": "2024-09-15T00:00:00Z",
            "deploymentUrl": "https://foundry-cardiac.openai.azure.com/deployments/medical-notes"
        },
        {
            "modelId": "fm-002",
            "name": "Phi-3 for Clinical Decision Support",
            "baseModel": "phi-3-medium",
            "version": "v2.0",
            "status": "Training",
            "progress": 75,
            "trainingDataset": "Clinical Guidelines Dataset",
            "estimatedCompletion": "2024-10-25T00:00:00Z"
        }
    ]

@app.post("/api/v1/foundry/models/{model_id}/deploy")
async def deploy_foundry_model(model_id: str):
    return {
        "modelId": model_id,
        "deploymentId": f"deploy-{uuid.uuid4()}",
        "status": "Deploying",
        "estimatedTime": "10-15 minutes",
        "endpoint": f"https://foundry-cardiac.openai.azure.com/deployments/{model_id}"
    }

@app.get("/api/v1/foundry/evaluations")
async def get_foundry_evaluations():
    return [
        {
            "evaluationId": "eval-001",
            "modelId": "fm-001",
            "modelName": "GPT-4o Fine-tuned for Medical Notes",
            "metrics": {
                "accuracy": 0.92,
                "precision": 0.91,
                "recall": 0.93,
                "f1Score": 0.92,
                "perplexity": 12.5
            },
            "testDataset": "Medical Notes Test Set",
            "evaluatedAt": "2024-09-20T00:00:00Z"
        }
    ]

@app.get("/api/v1/admin/users")
async def get_users():
    return [
        {
            "userId": "user-001",
            "email": "dr.smith@contosohealth.com",
            "name": "Dr. Sarah Smith",
            "role": "PI",
            "institution": "ContosoHealth Orlando",
            "accountType": "Staff",
            "status": "Active",
            "projects": 2,
            "lastLogin": "2024-10-19T14:30:00Z",
            "createdAt": "2024-01-10T00:00:00Z"
        },
        {
            "userId": "user-002",
            "email": "researcher@external.edu",
            "name": "Dr. John Doe",
            "role": "Contributor",
            "institution": "External University",
            "accountType": "Guest",
            "status": "Active",
            "projects": 1,
            "accessExpires": "2025-01-15T00:00:00Z",
            "lastLogin": "2024-10-18T09:30:00Z",
            "createdAt": "2024-03-01T00:00:00Z"
        }
    ]

@app.post("/api/v1/admin/users/invite")
async def invite_user(email: str, role: str, projectId: str):
    return {
        "invitationId": f"inv-{uuid.uuid4()}",
        "email": email,
        "role": role,
        "projectId": projectId,
        "status": "Sent",
        "expiresAt": (datetime.now() + timedelta(days=7)).isoformat(),
        "invitationUrl": f"https://research.contosohealth.com/invite/{uuid.uuid4()}"
    }

@app.get("/api/v1/admin/audit")
async def get_audit_logs(startDate: Optional[str] = None, endDate: Optional[str] = None):
    return [
        {
            "auditId": "audit-001",
            "userId": "user-001",
            "userEmail": "dr.smith@contosohealth.com",
            "action": "DatasetAccessed",
            "resource": "ECG Recordings Database",
            "resourceId": "ds-001",
            "projectId": "proj-001",
            "timestamp": "2024-10-19T14:30:00Z",
            "ipAddress": "10.0.1.25",
            "userAgent": "Mozilla/5.0",
            "result": "Success"
        },
        {
            "auditId": "audit-002",
            "userId": "user-002",
            "userEmail": "researcher@external.edu",
            "action": "ExportRequested",
            "resource": "ECG Recordings Database",
            "resourceId": "ds-001",
            "projectId": "proj-001",
            "timestamp": "2024-10-18T09:30:00Z",
            "ipAddress": "203.0.113.45",
            "userAgent": "Mozilla/5.0",
            "result": "Pending Approval"
        }
    ]
