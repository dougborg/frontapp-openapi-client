from enum import StrEnum


class AnalyticsActivitiesSmartQAScoreParameters(StrEnum):
    ADAPTABILITY = "Adaptability"
    ADAPTIVE_TONE = "Adaptive_Tone"
    BREVITY = "Brevity"
    COGNITIVE_EMPATHY = "Cognitive_Empathy"
    COMPASSIONATE_EMPATHY = "Compassionate_Empathy"
    COMPREHENSION = "Comprehension"
    DEMO_OFFERED = "Demo_Offered"
    EMOTIONAL_EMPATHY = "Emotional_Empathy"
    FRIENDLY = "Friendly"
    GENERAL_EMPATHY = "General_Empathy"
    GRAMMAR_SPELLING = "Grammar_Spelling"
    GREETING_OFFERED = "Greeting_Offered"
    INFORMATION_GATHERING = "Information_Gathering"
    NEUTRAL_TONE = "Neutral_Tone"
    PERSONALISATION = "Personalisation"
    POSITIVE_TONE = "Positive_Tone"
    PROFESSIONALISM = "Professionalism"
    PROFESSIONAL_BEHAVIOR = "Professional_Behavior"
    PROFESSIONAL_RELATIONSHIP = "Professional_Relationship"
    READABILITY = "Readability"
    SOLUTION_OFFERED = "Solution_Offered"
    TONE = "Tone"
    UPSELL = "Upsell"

    def __str__(self) -> str:
        return str(self.value)
