resource "aws_iam_role" "bedrock_agent_role" {
  name = "AmazonBedrockExecutionRoleForAgents_${var.project_name}-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "bedrock_agent_model_policy" {
  name = "BedrockAgentModelPolicy"
  role = aws_iam_role.bedrock_agent_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "bedrock:InvokeModel"
        Effect = "Allow"
        Resource = "arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
      },
      {
        Action = [
          "bedrock:InvokeAgent",
          "bedrock:GetAgentAlias"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:agent/*",
          "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:agent-alias/*"
        ]
      }
    ]
  })
}

# --- Sub-Agents ---

resource "aws_bedrockagent_agent" "activity_agent" {
  agent_name                  = "${var.project_name}-activity-agent-${var.environment}"
  agent_resource_role_arn     = aws_iam_role.bedrock_agent_role.arn
  agent_collaboration         = "DISABLED"
  idle_session_ttl_in_seconds = 1800
  foundation_model            = "anthropic.claude-sonnet-4-5-20250929-v1:0"
  instruction                 = "You are the Activity Specialist. Analyze physical activity data including steps, workouts, and caloric burn. Provide insights on training load, movement quality, and activity goals."
}

resource "aws_bedrockagent_agent_alias" "activity_agent_alias" {
  agent_id         = aws_bedrockagent_agent.activity_agent.id
  agent_alias_name = "v1"
  description      = "Initial version of activity agent"
}

resource "aws_bedrockagent_agent" "vitals_agent" {
  agent_name                  = "${var.project_name}-vitals-agent-${var.environment}"
  agent_resource_role_arn     = aws_iam_role.bedrock_agent_role.arn
  agent_collaboration         = "DISABLED"
  idle_session_ttl_in_seconds = 1800
  foundation_model            = "anthropic.claude-sonnet-4-5-20250929-v1:0"
  instruction                 = "You are the Vitals Specialist. Analyze biometric data including Heart Rate, HRV, SpO2, and Sleep Stages. Detect anomalies, assess physiological recovery, and explain health metrics clearly."
}

resource "aws_bedrockagent_agent_alias" "vitals_agent_alias" {
  agent_id         = aws_bedrockagent_agent.vitals_agent.id
  agent_alias_name = "v1"
  description      = "Initial version of vitals agent"
}

resource "aws_bedrockagent_agent" "wellbeing_agent" {
  agent_name                  = "${var.project_name}-wellbeing-agent-${var.environment}"
  agent_resource_role_arn     = aws_iam_role.bedrock_agent_role.arn
  agent_collaboration         = "DISABLED"
  idle_session_ttl_in_seconds = 1800
  foundation_model            = "anthropic.claude-sonnet-4-5-20250929-v1:0"
  instruction                 = "You are the Wellbeing Specialist. Focus on the user's holistic state, including Stress levels, Mood logs, and Energy budget (Spoon Theory). Provide psychological support and lifestyle balance advice."
}

resource "aws_bedrockagent_agent_alias" "wellbeing_agent_alias" {
  agent_id         = aws_bedrockagent_agent.wellbeing_agent.id
  agent_alias_name = "v1"
  description      = "Initial version of wellbeing agent"
}

# --- Supervisor Agent ---

resource "aws_bedrockagent_agent" "supervisor_agent" {
  agent_name                  = "${var.project_name}-supervisor-agent-${var.environment}"
  agent_resource_role_arn     = aws_iam_role.bedrock_agent_role.arn
  agent_collaboration         = "SUPERVISOR"
  idle_session_ttl_in_seconds = 1800
  foundation_model            = "anthropic.claude-sonnet-4-5-20250929-v1:0"
  instruction                 = "You are the Lead Health Coach Orchestrator. Your goal is to manage the user's health journey by delegating analysis to your specialized sub-agents (Activity, Vitals, Wellbeing). 1. Receive user queries or data events. 2. Consult the relevant sub-agent(s) for deep analysis. 3. Synthesize their findings. You MUST output your final analysis in strict JSON format with the following keys: 'state' (Enum: HAPPY, TIRED, STRESS, SICKNESS, EXERCISE, ANXIOUS, NEUTRAL), 'mood' (String), 'reasoning' (String: a concise summary for the user)."
  prepare_agent               = false
}

resource "aws_bedrockagent_agent_alias" "supervisor_agent_alias" {
  agent_id         = aws_bedrockagent_agent.supervisor_agent.id
  agent_alias_name = "live"
  description      = "Live version of the supervisor agent"
}

# --- Collaborator Links ---

resource "aws_bedrockagent_agent_collaborator" "supervisor_activity_collab" {
  agent_id                   = aws_bedrockagent_agent.supervisor_agent.id
  collaboration_instruction  = "Consult the Activity Specialist for questions regarding workouts, steps, calories, or physical strain."
  collaborator_name          = "ActivitySpecialist"
  relay_conversation_history = "TO_COLLABORATOR"

  agent_descriptor {
    alias_arn = aws_bedrockagent_agent_alias.activity_agent_alias.agent_alias_arn
  }
  prepare_agent = false
}

resource "aws_bedrockagent_agent_collaborator" "supervisor_vitals_collab" {
  agent_id                   = aws_bedrockagent_agent.supervisor_agent.id
  collaboration_instruction  = "Consult the Vitals Specialist for analysis of Heart Rate, HRV, Sleep data, or physiological recovery."
  collaborator_name          = "VitalsSpecialist"
  relay_conversation_history = "TO_COLLABORATOR"

  agent_descriptor {
    alias_arn = aws_bedrockagent_agent_alias.vitals_agent_alias.agent_alias_arn
  }
  prepare_agent = false
}

resource "aws_bedrockagent_agent_collaborator" "supervisor_wellbeing_collab" {
  agent_id                   = aws_bedrockagent_agent.supervisor_agent.id
  collaboration_instruction  = "Consult the Wellbeing Specialist for advice on stress, mood, mental energy, or general lifestyle balance."
  collaborator_name          = "WellbeingSpecialist"
  relay_conversation_history = "TO_COLLABORATOR"

  agent_descriptor {
    alias_arn = aws_bedrockagent_agent_alias.wellbeing_agent_alias.agent_alias_arn
  }
  prepare_agent = false
}