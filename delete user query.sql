BEGIN;

-- 1. Delete email-verification tokens belonging to users
DELETE FROM email_verification_tokens;

-- 2. Delete password-reset tokens belonging to users
DELETE FROM password_reset_tokens;

-- 3. Remove users from organizations
DELETE FROM organization_memberships;

-- 4. Remove invitations created by users
DELETE FROM organization_invitations;

-- 5. Delete the users themselves
DELETE FROM users;

-- Check what remains
SELECT COUNT(*) AS remaining_users FROM users;
SELECT COUNT(*) AS remaining_email_tokens FROM email_verification_tokens;
SELECT COUNT(*) AS remaining_reset_tokens FROM password_reset_tokens;
SELECT COUNT(*) AS remaining_memberships FROM organization_memberships;
SELECT COUNT(*) AS remaining_invitations FROM organization_invitations;