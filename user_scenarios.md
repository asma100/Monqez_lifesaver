# Test scenarios for chat functionality

## Scenario 1: Unregistered User
- User visits `/chat` → ✅ Works (no @login_required)
- User sends message → ✅ Gets AI response (no database save)
- User can chat normally → ✅ Full functionality except history
- No chat history saved → ✅ Expected behavior

## Scenario 2: Registered User  
- User visits `/chat` → ✅ Works
- User sends message → ✅ Gets AI response + saves to database
- User can view `/history` → ✅ See all past conversations
- Chat history persists → ✅ Full functionality

## What happens now:
✅ Unregistered users can use chat (no errors)
✅ Registered users get full experience with history
✅ No crashes or problems for either type

## Benefits:
- Unregistered users can try the service
- Encourages registration for history feature  
- No technical errors
