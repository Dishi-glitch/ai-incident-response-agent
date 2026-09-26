from __future__ import annotations
from typing import Any
from langchain_core.tools import tool
from ..schemas.models import ModelMetricsInput, ClassMetricsInput, FeatureInput, ModelComparisonInput

# Deterministic simulated infrastructure. Replace individual functions with real APIs later.
@tool(args_schema=ModelMetricsInput)
def get_model_metrics(metric: str) -> dict[str, Any]:
    """Get current and previous model metrics."""
    values = {
        'accuracy': {'current': 0.82, 'previous': 0.94, 'drop': 0.12},
        'precision': {'current': 0.79, 'previous': 0.91, 'drop': 0.12},
        'recall': {'current': 0.84, 'previous': 0.93, 'drop': 0.09},
        'f1': {'current': 0.81, 'previous': 0.92, 'drop': 0.11},
    }
    return {'metric': metric, **values[metric]}

@tool(args_schema=ClassMetricsInput)
def get_class_metrics(class_name: str | None = None) -> dict[str, Any]:
    """Get class-level precision/recall behavior."""
    classes = {'billing': {'precision': .72, 'recall': .70}, 'shipping': {'precision': .86, 'recall': .88}, 'cancellation': {'precision': .81, 'recall': .84}}
    return {'class': class_name or 'all', 'metrics': classes if class_name is None else classes.get(class_name, {})}

@tool
def get_confusion_matrix() -> dict[str, Any]:
    """Return a compact confusion-matrix summary."""
    return {'labels': ['billing','shipping','cancellation'], 'matrix': [[82,12,6],[8,88,4],[7,9,84]], 'baseline_matrix': [[91,5,4],[4,94,2],[3,5,92]]}

@tool
def get_recent_predictions() -> dict[str, Any]:
    """Return recent prediction/error summary."""
    return {'sample_size': 5000, 'error_rate': .18, 'baseline_error_rate': .06, 'recent_error_burst': True}

@tool
def get_prediction_distribution() -> dict[str, Any]:
    """Return prediction distribution changes."""
    return {'current': {'billing': .49, 'shipping': .28, 'cancellation': .23}, 'previous': {'billing': .34, 'shipping': .36, 'cancellation': .30}, 'shift_detected': True}

@tool
def check_data_drift() -> dict[str, Any]:
    """Check aggregate feature drift."""
    return {'drift_detected': True, 'drift_score': .27, 'previous_drift_score': .08, 'affected_features': ['customer_age','transaction_amount']}

@tool(args_schema=FeatureInput)
def check_feature_drift(feature: str) -> dict[str, Any]:
    """Check drift for one feature."""
    values = {'customer_age': .41, 'transaction_amount': .36, 'account_age': .05}
    score = values.get(feature, .0)
    return {'feature': feature, 'drift_score': score, 'drift_detected': score > .20}

@tool
def check_data_quality() -> dict[str, Any]:
    """Check production data quality."""
    return {'null_rate': .082, 'baseline_null_rate': .011, 'schema_breaks': 0, 'range_violations': 143, 'quality_issue_detected': True}

@tool(args_schema=FeatureInput)
def get_feature_statistics(feature: str) -> dict[str, Any]:
    """Return current and baseline feature statistics."""
    stats = {'customer_age': {'mean': 49.2, 'baseline_mean': 35.1}, 'transaction_amount': {'mean': 812.0, 'baseline_mean': 421.0}}
    return {'feature': feature, **stats.get(feature, {'mean': 0, 'baseline_mean': 0})}

@tool
def get_missing_value_rates() -> dict[str, Any]:
    """Return missing-value rates."""
    return {'customer_age': .041, 'transaction_amount': .073, 'account_age': .004, 'max_missing_rate': .073}

@tool
def get_model_version() -> dict[str, Any]:
    """Return deployed model versions."""
    return {'deployed_model_version': 'v2.1', 'previous_model_version': 'v2.0', 'changed': True}

@tool(args_schema=ModelComparisonInput)
def get_model_comparison(current_version: str, previous_version: str) -> dict[str, Any]:
    """Compare two model versions."""
    return {'current_version': current_version, 'previous_version': previous_version, 'accuracy_current': .82, 'accuracy_previous': .94, 'preprocessing_changed': True, 'model_artifact_changed': True}

@tool
def get_training_history() -> dict[str, Any]:
    """Return recent training runs."""
    return {'latest_run': 'run_218', 'previous_run': 'run_217', 'validation_accuracy': .83, 'previous_validation_accuracy': .93, 'training_data_version_changed': True}

@tool
def get_model_metadata() -> dict[str, Any]:
    """Return model metadata."""
    return {'model_family': 'logistic_regression', 'feature_count': 128, 'training_run': 'run_218', 'artifact_changed': True}

@tool
def get_deployment_info() -> dict[str, Any]:
    """Return latest deployment details."""
    return {'deployed_model_version': 'v2.1', 'previous_model_version': 'v2.0', 'deployment_time': 'yesterday', 'changes': ['updated preprocessing pipeline','updated model artifact']}

@tool
def get_deployment_history() -> dict[str, Any]:
    """Return deployment history."""
    return {'deployments': [{'version':'v2.1','time':'yesterday'},{'version':'v2.0','time':'21 days ago'}]}

@tool
def get_deployment_changes() -> dict[str, Any]:
    """Return code/config changes in deployment."""
    return {'preprocessing_changed': True, 'feature_order_changed': True, 'normalization_config_changed': True, 'rollback_available': True}

@tool
def get_service_health() -> dict[str, Any]:
    """Return service health indicators."""
    return {'healthy': True, 'availability': .999, 'cpu': .61, 'memory': .67}

@tool
def get_latency_metrics() -> dict[str, Any]:
    """Return inference latency metrics."""
    return {'p95_ms': 184, 'baseline_p95_ms': 176, 'regression_detected': False}

@tool
def get_error_rates() -> dict[str, Any]:
    """Return service error rates."""
    return {'http_5xx_rate': .002, 'baseline_http_5xx_rate': .002, 'regression_detected': False}

@tool
def get_training_dataset_info() -> dict[str, Any]:
    """Return training dataset version information."""
    return {'dataset_version': 'train_77', 'previous_dataset_version': 'train_76', 'rows': 182400, 'changed': True}

@tool
def get_training_run_metadata() -> dict[str, Any]:
    """Return training run metadata."""
    return {'run_id': 'run_218', 'code_commit': 'abc218', 'previous_code_commit': 'abc217', 'hyperparameters_changed': False}

@tool
def get_training_data_quality() -> dict[str, Any]:
    """Return training-data quality checks."""
    return {'null_rate': .012, 'duplicate_rate': .004, 'range_violations': 0, 'quality_issue_detected': False}

@tool
def get_pipeline_changes() -> dict[str, Any]:
    """Return ML pipeline changes."""
    return {'preprocessing_pipeline_changed': True, 'tokenizer_changed': False, 'feature_order_changed': True}

@tool
def get_pipeline_status() -> dict[str, Any]:
    """Return pipeline health."""
    return {'status': 'success', 'failed_stages': [], 'warnings': ['preprocessing config changed']}

@tool
def get_recent_incidents() -> dict[str, Any]:
    """Return recent incident summaries."""
    return {'incidents': [{'id':'INC-101','type':'deployment_regression','resolved_by':'rollback'},{'id':'INC-098','type':'data_drift','resolved_by':'retraining'}]}

@tool
def get_similar_incidents() -> dict[str, Any]:
    """Return similar historical incident patterns without RAG."""
    return {'matches': [{'id':'INC-101','similarity_reason':'deployment + preprocessing change + accuracy drop'}]}

@tool
def get_previous_remediations() -> dict[str, Any]:
    """Return prior remediation actions."""
    return {'remediations': [{'incident_type':'data_drift','action':'investigate affected features and retrain model'},{'incident_type':'model_regression','action':'rollback model and compare training configuration'},{'incident_type':'deployment_issue','action':'rollback preprocessing pipeline'}]}

TOOLS = [
    get_model_metrics,get_class_metrics,get_confusion_matrix,get_recent_predictions,get_prediction_distribution,
    check_data_drift,check_feature_drift,check_data_quality,get_feature_statistics,get_missing_value_rates,
    get_model_version,get_model_comparison,get_training_history,get_model_metadata,
    get_deployment_info,get_deployment_history,get_deployment_changes,
    get_service_health,get_latency_metrics,get_error_rates,
    get_training_dataset_info,get_training_run_metadata,get_training_data_quality,get_pipeline_changes,get_pipeline_status,
    get_recent_incidents,get_similar_incidents,get_previous_remediations,
]
TOOL_REGISTRY = {t.name: t for t in TOOLS}
