# Requirements Document

## Introduction

This document defines the requirements for PeachMine Discord Bot — a Discord bot for the "PeachMine" Minecraft server. The bot handles player applications through an interactive system using slash commands, buttons, and modals. It allows users to submit applications and administrators to review and process them.

## Glossary

- **Bot**: The PeachMine Discord bot application
- **User**: Any Discord server member who can submit applications
- **Admin**: The user with ADMIN_ID who can accept/reject applications
- **Application**: A player's request to join the Minecraft server containing personal information
- **Modal**: A Discord popup form for collecting user input
- **Embed**: A rich message format in Discord for displaying structured information
- **Ephemeral_Response**: A message visible only to the user who triggered it
- **Applications_Channel**: The Discord channel where application embeds are posted

## Requirements

### Requirement 1: Application Command

**User Story:** As a user, I want to initiate the application process using a slash command, so that I can apply to join the PeachMine Minecraft server.

#### Acceptance Criteria

1. WHEN a user executes the `/anketa` command, THE Bot SHALL respond with a message containing a "📋 Заполнить анкету" button
2. THE Bot SHALL make the `/anketa` command available to all server members
3. WHEN the `/anketa` command is executed, THE Bot SHALL respond with an ephemeral message

### Requirement 2: Application Modal System

**User Story:** As a user, I want to fill out an application form through modals, so that I can provide my information to join the server.

#### Acceptance Criteria

1. WHEN a user clicks the "📋 Заполнить анкету" button, THE Bot SHALL display the first modal with application questions
2. THE Bot SHALL collect the following information across modals:
   - Minecraft nickname
   - Age
   - Experience (text)
   - Why do you want to join us?
   - How much time are you willing to dedicate to the server?
3. IF all questions do not fit in one modal, THEN THE Bot SHALL split the application into two modals
4. WHEN the first modal is submitted and more questions remain, THE Bot SHALL display a "Продолжить" (Continue) button
5. WHEN the user clicks the "Продолжить" button, THE Bot SHALL display the second modal with remaining questions

### Requirement 3: Application Submission

**User Story:** As a user, I want my application to be submitted for review after completing all modals, so that administrators can process my request.

#### Acceptance Criteria

1. WHEN a user completes all application modals, THE Bot SHALL create an embed in the Applications_Channel
2. THE Bot SHALL include the following in the application embed:
   - Author information (username and user ID)
   - All answers from the application
3. THE Bot SHALL display "✅ Принять" (Accept) and "❌ Отклонить" (Reject) buttons under the embed
4. WHEN the application is submitted, THE Bot SHALL send an ephemeral confirmation to the user

### Requirement 4: Application Review

**User Story:** As an admin, I want to accept or reject applications, so that I can manage who joins the Minecraft server.

#### Acceptance Criteria

1. WHEN the Admin clicks the "✅ Принять" button, THE Bot SHALL send a DM to the applicant with "Анкета одобрена"
2. WHEN the Admin clicks the "❌ Отклонить" button, THE Bot SHALL send a DM to the applicant with "Анкета отклонена"
3. WHEN a non-admin user clicks Accept or Reject buttons, THE Bot SHALL respond with an ephemeral error message
4. THE Bot SHALL verify the user ID matches ADMIN_ID before processing review actions
5. WHEN an application is processed, THE Bot SHALL update the embed to reflect the decision status

### Requirement 5: Security and Error Handling

**User Story:** As a system administrator, I want the bot to handle errors gracefully and enforce access controls, so that the application system remains secure and reliable.

#### Acceptance Criteria

1. THE Bot SHALL use ephemeral responses for all user interactions except the application embed
2. IF an error occurs during any operation, THEN THE Bot SHALL log the error to console and respond with a user-friendly message
3. THE Bot SHALL validate that ADMIN_ID is set before processing review actions
4. IF the bot cannot send a DM to the applicant, THEN THE Bot SHALL log the error and notify the admin
5. THE Bot SHALL load configuration from environment variables (DISCORD_TOKEN, CLIENT_ID, GUILD_ID, ADMIN_ID, APPLICATIONS_CHANNEL_ID)

### Requirement 6: Project Structure and Code Quality

**User Story:** As a developer, I want the code to be well-organized and documented, so that I can maintain and extend the bot easily.

#### Acceptance Criteria

1. THE Bot SHALL organize code into the following structure:
   - index.js (main entry point)
   - commands/ (slash command definitions)
   - handlers/ (event handlers)
   - modals/ (modal definitions and handlers)
   - buttons/ (button handlers)
2. THE Bot SHALL include console logs for important events (startup, commands, errors)
3. THE Bot SHALL include code comments explaining key functionality
4. THE Bot SHALL use only current discord.js v14 API methods (no deprecated methods)
5. THE Bot SHALL include launch instructions in documentation
