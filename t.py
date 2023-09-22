import os
from dotenv import load_dotenv
import openai
from gpt_engineer.ai import AI
from gpt_engineer.chat_to_files import get_code_strings, overwrite_files
from gpt_engineer.db import DB, DBs
from gpt_engineer.file_selector import FILE_LIST_NAME, ask_for_files_checkov
from gpt_engineer.steps import curr_fn, setup_sys_prompt_existing_code

def set_improve_filelist_checkov(ai: AI, dbs: DBs):
    """Sets the file list for files to work with in existing code mode."""
    ask_for_files_checkov(dbs.input)  # stores files as full paths.
    file_list = dbs.input[FILE_LIST_NAME]
    return file_list


def get_improve_prompt_checkov(ai: AI, dbs: DBs, checkovResults):
    """
    Generates prompts for code improvement based on the checkovResults.
    """
    prompts = []

    for result in checkovResults:
        if result["check_result"]["result"] == "FAILED":
            fix_instructions = "\n".join(result.get("details", []))
            code_block = result.get("code_block", [])

            code_strings = [code_item[1] for code_item in code_block]  # Extract the code strings
            code_string = "\n".join(code_strings)

            prompt = f"Fix the code lines according to fix instructions: {fix_instructions}\n Code:\n{code_string}\n"
            prompts.append(prompt)

    dbs.input["prompt"] = prompts
    return []

def improve_existing_code_checkov(ai: AI, dbs: DBs):
    """
    After the file list and prompts have been acquired, this function is called
    to send the formatted prompts to the LLM and save the modified code.
    """

    prompts = dbs.input["prompt"]
    
    messages = []
    
    for prompt in prompts:
        messages.append(ai.fuser(f"Request: {prompt}"))

    messages = ai.next(messages, step_name=curr_fn())

    # Save the modified code
    modified_code = messages[-1].content.strip()
    print("MODIFIED CODE", modified_code)
    overwrite_files(modified_code, dbs)

    # return messages


ai = AI(
    model_name="infraBot",
    temperature=0.1,
    azure_endpoint="https://ai-ankur.openai.azure.com/"
)

body = {}

dbs = DBs(
    memory=DB(data=body, identifier='memory'),
    logs=DB(data=body, identifier='logs'),
    preprompts=DB(data=body, identifier='preprompts'),
    input=DB(data=body, identifier='input_prompt'),
    workspace=DB(data=body, identifier='workspace'),
    archive=DB(data=body, identifier='archive'),
    )

# file_list = set_improve_filelist_checkov(ai, dbs)
# print("File list", file_list)
checkov_results = [
    {
        "check_id": "CKV_GCP_28",
        "bc_check_id": "BC_GCP_PUBLIC_1",
        "check_name": "Ensure that Cloud Storage bucket is not anonymously or publicly accessible",
        "check_result": {
            "result": "FAILED",
            "evaluated_keys": [
                "members",
                "member"
            ]
        },
        "code_block": [
            [
                17,
                "resource \"google_storage_bucket_iam_binding\" \"allow_public_read\" {\n"
            ],
            [
                18,
                "  bucket  = google_storage_bucket.terragoat_website.id\n"
            ],
            [
                19,
                "  members = [\"allUsers\"]\n"
            ],
            [
                20,
                "  role    = \"roles/storage.objectViewer\"\n"
            ],
            [
                21,
                "}"
            ]
        ],
        "file_path": "/gcs.tf",
        "file_abs_path": "/tmp/tmp5tfpktte/gcs.tf",
        "repo_file_path": "/tmp/tmp5tfpktte/gcs.tf",
        "file_line_range": [
            17,
            21
        ],
        "resource": "google_storage_bucket_iam_binding.allow_public_read",
        "evaluations": None,
        "check_class": "checkov.terraform.checks.resource.gcp.GoogleStorageBucketNotPublic",
        "fixed_definition": None,
        "entity_tags": None,
        "caller_file_path": None,
        "caller_file_line_range": None,
        "resource_address": None,
        "severity": "HIGH",
        "bc_category": None,
        "benchmarks": None,
        "description": None,
        "short_description": None,
        "vulnerability_details": None,
        "connected_node": None,
        "guideline": "https://docs.paloaltonetworks.com/content/techdocs/en_US/prisma/prisma-cloud/prisma-cloud-code-security-policy-reference/google-cloud-policies/google-cloud-public-policies/bc-gcp-public-1.html",
        "details": [
            "",
            "**Why it is a problem?**.",
            "The code creates an IAM binding that grants the `roles/storage.objectViewer` role to `allUsers` on the specified Cloud Storage bucket.",
            "This means that anyone, including anonymous users, can view the objects in the bucket.",
            "This violates the policy of ensuring that Cloud Storage bucket is not anonymously or publicly accessible.",
            "The potential risk is that sensitive data stored in the bucket can be accessed by unauthorized users, leading to data breaches and other security incidents.",
            "",
            "**How to fix it**.",
            "To fix this issue, you should remove the `google_storage_bucket_iam_binding` resource that grants the `roles/storage.objectViewer` role to `allUsers`.",
            "Instead, you should create a new IAM binding that grants the necessary permissions to specific users or service accounts that require access to the bucket.",
            "You can also use Cloud Identity and Access Management (Cloud IAM) to set up fine-grained access control for your Cloud Storage buckets.",
            "This will ensure that only authorized users and services can access the data in the bucket."
        ],
        "check_len": None,
        "definition_context_file_path": "{\"file_path\": \"/tmp/tmp5tfpktte/gcs.tf\", \"tf_source_modules\": None}",
        "incidentType": "Violation",
        "category": "Public"
    },
    {
        "check_id": "CKV_GCP_62",
        "bc_check_id": "BC_GCP_GCS_3",
        "check_name": "Bucket should log access",
        "check_result": {
            "result": "FAILED",
            "evaluated_keys": [
                "logging/[0]/log_bucket"
            ]
        },
        "code_block": [
            [
                1,
                "resource \"google_storage_bucket\" \"terragoat_website\" {\n"
            ],
            [
                2,
                "  name          = \"terragot-${var.environment}\"\n"
            ],
            [
                3,
                "  location      = var.location\n"
            ],
            [
                4,
                "  force_destroy = true\n"
            ],
            [
                5,
                "  labels = {\n"
            ],
            [
                6,
                "    git_commit           = \"2bdc0871a5f4505be58244029cc6485d45d7bb8e\"\n"
            ],
            [
                7,
                "    git_file             = \"terraform__gcp__gcs_tf\"\n"
            ],
            [
                8,
                "    git_last_modified_at = \"2022-01-19-17-02-27\"\n"
            ],
            [
                9,
                "    git_last_modified_by = \"jameswoolfenden\"\n"
            ],
            [
                10,
                "    git_modifiers        = \"jameswoolfenden__nimrodkor\"\n"
            ],
            [
                11,
                "    git_org              = \"bridgecrewio\"\n"
            ],
            [
                12,
                "    git_repo             = \"terragoat\"\n"
            ],
            [
                13,
                "    yor_trace            = \"bd00cd2e-f53f-4daf-8d4d-74c47846c1cc\"\n"
            ],
            [
                14,
                "  }\n"
            ],
            [
                15,
                "}\n"
            ]
        ],
        "file_path": "/gcs.tf",
        "file_abs_path": "/tmp/tmp5tfpktte/gcs.tf",
        "repo_file_path": "/tmp/tmp5tfpktte/gcs.tf",
        "file_line_range": [
            1,
            15
        ],
        "resource": "google_storage_bucket.terragoat_website",
        "evaluations": None,
        "check_class": "checkov.terraform.checks.resource.gcp.CloudStorageLogging",
        "fixed_definition": None,
        "entity_tags": None,
        "caller_file_path": None,
        "caller_file_line_range": None,
        "resource_address": None,
        "severity": "INFO",
        "bc_category": None,
        "benchmarks": None,
        "description": None,
        "short_description": None,
        "vulnerability_details": None,
        "connected_node": None,
        "guideline": "https://docs.paloaltonetworks.com/content/techdocs/en_US/prisma/prisma-cloud/prisma-cloud-code-security-policy-reference/google-cloud-policies/google-cloud-storage-gcs-policies/bc-gcp-logging-2.html",
        "details": [
            "",
            "**Why it is a problem?**.",
            "The code creates a Google Cloud Storage bucket but does not enable access logging.",
            "Access logging is an essential security feature that helps to track and investigate unauthorized access attempts, data breaches, and other security incidents.",
            "Without access logging, it is difficult to detect and respond to security incidents, which can lead to data loss, theft, or other security breaches.",
            "",
            "**How to fix it**.",
            "To fix this issue, you should enable access logging for the Google Cloud Storage bucket.",
            "Access logging can be enabled by adding a `logging` block to the `google_storage_bucket` resource.",
            "The `logging` block should specify the destination bucket and object prefix for the access logs.",
            "You can also configure other options such as the log format and retention period.",
            "Once access logging is enabled, you can use Cloud Logging or other tools to monitor and analyze the access logs."
        ],
        "check_len": None,
        "definition_context_file_path": "{\"file_path\": \"/tmp/tmp5tfpktte/gcs.tf\", \"tf_source_modules\": None}",
        "incidentType": "Violation",
        "category": "Storage"
    },
    {
        "check_id": "CKV_GCP_78",
        "bc_check_id": "BC_GCP_GENERAL_39",
        "check_name": "Ensure Cloud storage has versioning enabled",
        "check_result": {
            "result": "FAILED",
            "evaluated_keys": [
                "versioning/[0]/enabled"
            ]
        },
        "code_block": [
            [
                1,
                "resource \"google_storage_bucket\" \"terragoat_website\" {\n"
            ],
            [
                2,
                "  name          = \"terragot-${var.environment}\"\n"
            ],
            [
                3,
                "  location      = var.location\n"
            ],
            [
                4,
                "  force_destroy = true\n"
            ],
            [
                5,
                "  labels = {\n"
            ],
            [
                6,
                "    git_commit           = \"2bdc0871a5f4505be58244029cc6485d45d7bb8e\"\n"
            ],
            [
                7,
                "    git_file             = \"terraform__gcp__gcs_tf\"\n"
            ],
            [
                8,
                "    git_last_modified_at = \"2022-01-19-17-02-27\"\n"
            ],
            [
                9,
                "    git_last_modified_by = \"jameswoolfenden\"\n"
            ],
            [
                10,
                "    git_modifiers        = \"jameswoolfenden__nimrodkor\"\n"
            ],
            [
                11,
                "    git_org              = \"bridgecrewio\"\n"
            ],
            [
                12,
                "    git_repo             = \"terragoat\"\n"
            ],
            [
                13,
                "    yor_trace            = \"bd00cd2e-f53f-4daf-8d4d-74c47846c1cc\"\n"
            ],
            [
                14,
                "  }\n"
            ],
            [
                15,
                "}\n"
            ]
        ],
        "file_path": "/gcs.tf",
        "file_abs_path": "/tmp/tmp5tfpktte/gcs.tf",
        "repo_file_path": "/tmp/tmp5tfpktte/gcs.tf",
        "file_line_range": [
            1,
            15
        ],
        "resource": "google_storage_bucket.terragoat_website",
        "evaluations": None,
        "check_class": "checkov.terraform.checks.resource.gcp.CloudStorageVersioningEnabled",
        "fixed_definition": None,
        "entity_tags": None,
        "caller_file_path": None,
        "caller_file_line_range": None,
        "resource_address": None,
        "severity": "LOW",
        "bc_category": None,
        "benchmarks": None,
        "description": None,
        "short_description": None,
        "vulnerability_details": None,
        "connected_node": None,
        "guideline": "https://docs.paloaltonetworks.com/content/techdocs/en_US/prisma/prisma-cloud/prisma-cloud-code-security-policy-reference/google-cloud-policies/google-cloud-general-policies/ensure-gcp-cloud-storage-has-versioning-enabled.html",
        "details": [
            "",
            "**Why it is a problem?**.",
            "The code creates a Google Cloud Storage bucket without enabling versioning.",
            "Versioning is a feature that allows you to store multiple versions of an object in the same bucket.",
            "Without versioning, if an object is accidentally deleted or overwritten, it cannot be recovered.",
            "This can lead to data loss and potential compliance violations.",
            "",
            "**How to fix it**.",
            "To fix this issue, you should enable versioning for the Google Cloud Storage bucket.",
            "This can be done by adding the `versioning` block to the `google_storage_bucket` resource and setting the `enabled` attribute to `true`.",
            "Additionally, you may want to consider setting a retention policy to ensure that versions of objects are retained for a specified period of time."
        ],
        "check_len": None,
        "definition_context_file_path": "{\"file_path\": \"/tmp/tmp5tfpktte/gcs.tf\", \"tf_source_modules\": None}",
        "incidentType": "Violation",
        "category": "General"
    },
    {
        "check_id": "CKV_GCP_29",
        "bc_check_id": "BC_GCP_GCS_2",
        "check_name": "Ensure that Cloud Storage buckets have uniform bucket-level access enabled",
        "check_result": {
            "result": "FAILED",
            "evaluated_keys": [
                "uniform_bucket_level_access"
            ]
        },
        "code_block": [
            [
                1,
                "resource \"google_storage_bucket\" \"terragoat_website\" {\n"
            ],
            [
                2,
                "  name          = \"terragot-${var.environment}\"\n"
            ],
            [
                3,
                "  location      = var.location\n"
            ],
            [
                4,
                "  force_destroy = true\n"
            ],
            [
                5,
                "  labels = {\n"
            ],
            [
                6,
                "    git_commit           = \"2bdc0871a5f4505be58244029cc6485d45d7bb8e\"\n"
            ],
            [
                7,
                "    git_file             = \"terraform__gcp__gcs_tf\"\n"
            ],
            [
                8,
                "    git_last_modified_at = \"2022-01-19-17-02-27\"\n"
            ],
            [
                9,
                "    git_last_modified_by = \"jameswoolfenden\"\n"
            ],
            [
                10,
                "    git_modifiers        = \"jameswoolfenden__nimrodkor\"\n"
            ],
            [
                11,
                "    git_org              = \"bridgecrewio\"\n"
            ],
            [
                12,
                "    git_repo             = \"terragoat\"\n"
            ],
            [
                13,
                "    yor_trace            = \"bd00cd2e-f53f-4daf-8d4d-74c47846c1cc\"\n"
            ],
            [
                14,
                "  }\n"
            ],
            [
                15,
                "}\n"
            ]
        ],
        "file_path": "/gcs.tf",
        "file_abs_path": "/tmp/tmp5tfpktte/gcs.tf",
        "repo_file_path": "/tmp/tmp5tfpktte/gcs.tf",
        "file_line_range": [
            1,
            15
        ],
        "resource": "google_storage_bucket.terragoat_website",
        "evaluations": None,
        "check_class": "checkov.terraform.checks.resource.gcp.GoogleStorageBucketUniformAccess",
        "fixed_definition": None,
        "entity_tags": None,
        "caller_file_path": None,
        "caller_file_line_range": None,
        "resource_address": None,
        "severity": "LOW",
        "bc_category": None,
        "benchmarks": None,
        "description": None,
        "short_description": None,
        "vulnerability_details": None,
        "connected_node": None,
        "guideline": "https://docs.paloaltonetworks.com/content/techdocs/en_US/prisma/prisma-cloud/prisma-cloud-code-security-policy-reference/google-cloud-policies/google-cloud-storage-gcs-policies/bc-gcp-gcs-2.html",
        "details": [
            "",
            "**Why it is a problem?**.",
            "The code creates a Google Cloud Storage bucket without enabling uniform bucket-level access.",
            "This means that access to the bucket is controlled by Access Control Lists (ACLs) on individual objects within the bucket, rather than by a uniform policy applied to the bucket as a whole.",
            "This can lead to inconsistent access control policies and make it difficult to manage access to the bucket.",
            "It also increases the risk of misconfiguration and unauthorized access to sensitive data stored in the bucket.",
            "",
            "**How to fix it**.",
            "To fix this issue, you should enable uniform bucket-level access for the Google Cloud Storage bucket.",
            "This can be done by setting the `uniform_bucket_level_access` attribute to `true` in the `google_storage_bucket` resource block.",
            "This ensures that access to the bucket is controlled by a uniform policy applied to the bucket as a whole, rather than by ACLs on individual objects within the bucket.",
            "Additionally, you should review and update the bucket's IAM policies to ensure that only authorized users and services have access to the bucket and its contents."
        ],
        "check_len": None,
        "definition_context_file_path": "{\"file_path\": \"/tmp/tmp5tfpktte/gcs.tf\", \"tf_source_modules\": None}",
        "incidentType": "Violation",
        "category": "Storage"
    },
    {
        "check_id": "CKV_GCP_114",
        "bc_check_id": None,
        "check_name": "Ensure public access prevention is enforced on Cloud Storage bucket",
        "check_result": {
            "result": "FAILED",
            "evaluated_keys": [
                "public_access_prevention"
            ]
        },
        "code_block": [
            [
                1,
                "resource \"google_storage_bucket\" \"terragoat_website\" {\n"
            ],
            [
                2,
                "  name          = \"terragot-${var.environment}\"\n"
            ],
            [
                3,
                "  location      = var.location\n"
            ],
            [
                4,
                "  force_destroy = true\n"
            ],
            [
                5,
                "  labels = {\n"
            ],
            [
                6,
                "    git_commit           = \"2bdc0871a5f4505be58244029cc6485d45d7bb8e\"\n"
            ],
            [
                7,
                "    git_file             = \"terraform__gcp__gcs_tf\"\n"
            ],
            [
                8,
                "    git_last_modified_at = \"2022-01-19-17-02-27\"\n"
            ],
            [
                9,
                "    git_last_modified_by = \"jameswoolfenden\"\n"
            ],
            [
                10,
                "    git_modifiers        = \"jameswoolfenden__nimrodkor\"\n"
            ],
            [
                11,
                "    git_org              = \"bridgecrewio\"\n"
            ],
            [
                12,
                "    git_repo             = \"terragoat\"\n"
            ],
            [
                13,
                "    yor_trace            = \"bd00cd2e-f53f-4daf-8d4d-74c47846c1cc\"\n"
            ],
            [
                14,
                "  }\n"
            ],
            [
                15,
                "}\n"
            ]
        ],
        "file_path": "/gcs.tf",
        "file_abs_path": "/tmp/tmp5tfpktte/gcs.tf",
        "repo_file_path": "/tmp/tmp5tfpktte/gcs.tf",
        "file_line_range": [
            1,
            15
        ],
        "resource": "google_storage_bucket.terragoat_website",
        "evaluations": None,
        "check_class": "checkov.terraform.checks.resource.gcp.GoogleStoragePublicAccessPrevention",
        "fixed_definition": None,
        "entity_tags": None,
        "caller_file_path": None,
        "caller_file_line_range": None,
        "resource_address": None,
        "severity": "Unknown",
        "bc_category": None,
        "benchmarks": {},
        "description": None,
        "short_description": None,
        "vulnerability_details": None,
        "connected_node": None,
        "guideline": None,
        "details": [
            "",
            "**Why it is a problem?**.",
            "The code creates a Google Cloud Storage bucket without any public access prevention mechanism.",
            "This means that anyone with the bucket's name can access its contents, which can lead to unauthorized access, data leakage, and other security risks.",
            "",
            "**How to fix it**.",
            "To prevent public access to the bucket, you can set the `allUsers` and `allAuthenticatedUsers` members to `none` for the `google_storage_bucket_iam_binding` resource.",
            "This will ensure that only authorized users and services can access the bucket.",
            "Additionally, you can enable object versioning and configure lifecycle rules to automatically delete or archive objects after a certain period.",
            "Finally, you can enable logging and monitoring to detect and respond to any suspicious activity."
        ],
        "check_len": None,
        "definition_context_file_path": "{\"file_path\": \"/tmp/tmp5tfpktte/gcs.tf\", \"tf_source_modules\": None}",
        "incidentType": "Unknown",
        "category": "Unknown"
    }
]
get_improve_prompt_checkov(ai, dbs, checkov_results)
improve_existing_code_checkov(ai, dbs)
