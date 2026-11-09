# Maintained by Mei Qi (2605039)
# Base class for all AI manager errors
class AIError(Exception):
    pass

# The API output is unusable, and it is also the parent of the specific cases below
class InvalidAIOutputError(AIError):
    pass

# The api output was not valid JSON
class MalformedJSONError(InvalidAIOutputError):
    pass

# The AI output did not follow the defined response schema
class SchemaViolationError(InvalidAIOutputError):
    pass

# The same shelter appeared more than once in the AI output
class DuplicateShelterError(InvalidAIOutputError):
    pass

# All attempts to get a valid API response failed
class AIServiceError(AIError):
    pass