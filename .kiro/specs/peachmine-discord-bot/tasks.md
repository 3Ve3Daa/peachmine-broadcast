# Implementation Plan: PeachMine Discord Bot

## Overview

This plan implements the PeachMine Discord bot using Node.js and discord.js v14. Tasks are organized to build incrementally: project setup → core utilities → command → buttons → modals → integration.

## Tasks

- [ ] 1. Project setup and configuration
  - [x] 1.1 Initialize Node.js project with package.json and install dependencies (discord.js, dotenv)
    - Create package.json with name, version, main entry point
    - Install discord.js v14 and dotenv
    - Create .env.example with all required variables
    - _Requirements: 5.5, 6.1_
  - [x] 1.2 Create project directory structure
    - Create folders: commands/, handlers/, modals/, buttons/, utils/
    - _Requirements: 6.1_
  - [x] 1.3 Implement utils/config.js with environment variable loading and validation
    - Load all env variables (DISCORD_TOKEN, CLIENT_ID, GUILD_ID, ADMIN_ID, APPLICATIONS_CHANNEL_ID)
    - Implement validate() function that throws on missing variables
    - _Requirements: 5.3, 5.5_
  - [ ]* 1.4 Write property test for config validation
    - **Property 8: Configuration Validation**
    - Test that any missing required variable causes validation to throw
    - **Validates: Requirements 5.3, 5.5**

- [ ] 2. Core utilities implementation
  - [x] 2.1 Implement utils/applicationStore.js for temporary application data storage
    - Implement setPartial(userId, data) to store partial application
    - Implement getPartial(userId) to retrieve partial data
    - Implement complete(userId) to get and remove data
    - _Requirements: 2.4, 3.1_
  - [ ]* 2.2 Write property test for application store round-trip
    - **Property 4: Application Data Round-Trip**
    - Test that setPartial then getPartial returns equivalent data
    - **Validates: Requirements 2.4, 3.1**
  - [x] 2.3 Implement utils/embedBuilder.js for creating application embeds
    - Create createApplicationEmbed(data) function
    - Include all fields: username, userId, nickname, age, experience, whyJoin, timeDedication
    - Add Accept/Reject buttons with applicant userId in customId
    - _Requirements: 3.2, 3.3_
  - [ ]* 2.4 Write property test for embed completeness
    - **Property 5: Embed Contains All Application Data**
    - Test that generated embed contains all required fields for any valid input
    - **Validates: Requirements 3.2, 3.3**

- [x] 3. Checkpoint - Verify utilities
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Bot entry point and interaction handler
  - [x] 4.1 Implement index.js with Discord client setup and handler loading
    - Create client with required intents (Guilds, GuildMessages)
    - Set up Collections for commands, buttons, modals
    - Implement loader functions for each handler type
    - Register slash commands on ready event
    - _Requirements: 6.1, 6.2_
  - [x] 4.2 Implement handlers/interactionHandler.js for routing interactions
    - Route ChatInputCommand to commands collection
    - Route Button interactions to buttons collection (parse customId)
    - Route ModalSubmit to modals collection (parse customId)
    - Implement error handling with user-friendly messages
    - _Requirements: 5.2, 6.1_
  - [ ]* 4.3 Write property test for error handling
    - **Property 9: Error Handling Returns User-Friendly Message**
    - Test that errors result in Russian user-friendly message
    - **Validates: Requirements 5.2**

- [ ] 5. Slash command implementation
  - [x] 5.1 Implement commands/anketa.js slash command
    - Define SlashCommandBuilder with name 'anketa' and Russian description
    - Create execute function that replies with ephemeral message
    - Include "📋 Заполнить анкету" button in response
    - Add console log for command execution
    - _Requirements: 1.1, 1.2, 1.3, 6.2_
  - [ ]* 5.2 Write property test for command response
    - **Property 1: Command Response Contains Button**
    - **Property 2: All Responses Are Ephemeral**
    - Test response contains button and is ephemeral
    - **Validates: Requirements 1.1, 1.3, 5.1**

- [ ] 6. Button handlers implementation
  - [x] 6.1 Implement buttons/fillApplication.js
    - Create modal with customId 'application_modal_1:{userId}'
    - Add fields: minecraft_nickname (Short), age (Short), experience (Paragraph)
    - Show modal on button click
    - Add console log
    - _Requirements: 2.1, 2.2_
  - [x] 6.2 Implement buttons/continueApplication.js
    - Create modal with customId 'application_modal_2:{userId}'
    - Add fields: why_join (Paragraph), time_dedication (Short)
    - Show modal on button click
    - Add console log
    - _Requirements: 2.5_
  - [x] 6.3 Implement buttons/acceptApplication.js
    - Verify user.id === ADMIN_ID, return ephemeral error if not
    - Extract applicantId from customId
    - Send DM "Анкета одобрена" to applicant
    - Update embed with green color and approval footer
    - Remove buttons from embed
    - Handle DM failure gracefully
    - _Requirements: 4.1, 4.3, 4.4, 4.5, 5.4_
  - [x] 6.4 Implement buttons/rejectApplication.js
    - Verify user.id === ADMIN_ID, return ephemeral error if not
    - Extract applicantId from customId
    - Send DM "Анкета отклонена" to applicant
    - Update embed with red color and rejection footer
    - Remove buttons from embed
    - Handle DM failure gracefully
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 5.4_
  - [ ]* 6.5 Write property test for admin access control
    - **Property 6: Admin Access Control**
    - Test that non-admin users receive ephemeral error
    - **Validates: Requirements 4.3, 4.4**

- [ ] 7. Modal handlers implementation
  - [x] 7.1 Implement modals/applicationModal1.js
    - Extract fields: minecraft_nickname, age, experience
    - Store partial data in applicationStore with userId
    - Reply with ephemeral message and "Продолжить" button
    - Add console log
    - _Requirements: 2.2, 2.4_
  - [x] 7.2 Implement modals/applicationModal2.js
    - Retrieve partial data from applicationStore
    - Handle missing data (ask user to restart)
    - Extract fields: why_join, time_dedication
    - Complete application data
    - Send embed to APPLICATIONS_CHANNEL_ID
    - Reply with ephemeral confirmation
    - Add console log
    - _Requirements: 2.2, 2.5, 3.1, 3.4_
  - [ ]* 7.3 Write property test for modal fields completeness
    - **Property 3: Modal Fields Completeness**
    - Test that both modals together collect all 5 required fields
    - **Validates: Requirements 2.2**

- [x] 8. Checkpoint - Full integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Documentation and final touches
  - [x] 9.1 Create README.md with setup and launch instructions
    - Document environment variables
    - Include installation steps (npm install)
    - Include bot invite instructions
    - Include launch command (node index.js)
    - _Requirements: 6.5_
  - [x] 9.2 Add code comments to all files
    - Add JSDoc comments to exported functions
    - Add inline comments for complex logic
    - _Requirements: 6.3_

- [x] 10. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- All user-facing messages are in Russian as specified
- Code comments and documentation are in English
- Each task references specific requirements for traceability
- Property tests use fast-check library with minimum 100 iterations
