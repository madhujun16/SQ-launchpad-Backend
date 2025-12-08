# GCP Deployment Permissions Guide

## Overview

This document outlines the required permissions and roles for deploying the Launchpad Backend application to Google Cloud Platform (GCP) App Engine.

## Current Deployment Issue

The deployment is currently blocked because the App Engine staging bucket (`staging.smartq-backend-784299.appspot.com`) does not exist and cannot be created via CLI due to domain verification requirements.

## Required IAM Roles

### For User Account Deployment

The following roles are required for the user account attempting deployment:

#### Minimum Required Roles:
1. **App Engine Admin** (`roles/appengine.appAdmin`)
   - Full control over App Engine applications
   - Can create and manage versions, services, and instances
   - Required for: Deploying applications, managing versions

2. **Storage Admin** (`roles/storage.admin`)
   - Full control over Cloud Storage buckets and objects
   - Required for: Creating staging buckets, uploading deployment files

#### Alternative (Higher Privilege):
- **Editor** (`roles/editor`)
  - Includes most permissions needed for deployment
  - Provides broader access to the project

### For Service Account Deployment

If using a service account (e.g., `launchpad@smartq-backend-784299.iam.gserviceaccount.com`):

#### Required Roles:
1. **App Engine Admin** (`roles/appengine.appAdmin`)
2. **Storage Admin** (`roles/storage.admin`)
3. **Service Account User** (`roles/iam.serviceAccountUser`)
   - Required if the service account needs to act as another service account

## Current Project Configuration

- **Project ID**: `smartq-backend-784299`
- **Project Number**: `464251598887`
- **Region**: `europe-west1`
- **App Engine Service**: `launchpad-backend`
- **Service Account**: `smartq-backend-784299@appspot.gserviceaccount.com`

## Required GCP APIs

The following APIs must be enabled:

1. **App Engine Admin API** (`appengine.googleapis.com`)
   - Required for App Engine deployments
   - Status: ✅ Enabled

2. **Cloud Storage API** (`storage-component.googleapis.com`)
   - Required for bucket operations
   - Status: ✅ Enabled

3. **Storage API** (`storage-api.googleapis.com`)
   - Required for storage operations
   - Status: ✅ Enabled

4. **Cloud Build API** (`cloudbuild.googleapis.com`)
   - Required if using Cloud Build for deployment
   - Status: Check via console

## Staging Bucket Requirements

### Required Bucket
- **Bucket Name**: `staging.smartq-backend-784299.appspot.com`
- **Location**: `europe-west1`
- **Purpose**: Stores deployment files before App Engine processes them

### Issue
The staging bucket cannot be created via CLI (`gcloud` or `gsutil`) because:
- The bucket name format (`*.appspot.com`) is treated as a domain
- Google requires domain verification for such bucket names
- Domain verification cannot be completed programmatically

### Solution
The staging bucket must be created through one of these methods:
1. **GCP Console** (Recommended)
   - App Engine automatically creates the bucket during first deployment via Console
   - Go to: https://console.cloud.google.com/appengine/services?project=smartq-backend-784299

2. **Manual Bucket Creation** (If needed)
   - Use GCP Console Storage browser
   - Create bucket: `staging.smartq-backend-784299.appspot.com`
   - Location: `europe-west1`
   - Note: May still require domain verification

## Service Account Permissions

### App Engine Default Service Account
- **Email**: `smartq-backend-784299@appspot.gserviceaccount.com`
- **Current Roles**: 
  - `roles/editor` (from IAM policy)
  - `roles/secretmanager.secretAccessor`

### Custom Service Account (if used)
- **Email**: `launchpad@smartq-backend-784299.iam.gserviceaccount.com`
- **Current Roles**: 
  - `roles/owner` (from IAM policy)

## Deployment Methods

### Method 1: GCP Console (Recommended for First Deployment)

**Why**: Automatically handles bucket creation and permissions

**Steps**:
1. Navigate to: https://console.cloud.google.com/appengine/services?project=smartq-backend-784299
2. Click "New Version" or "Deploy New Version"
3. Choose source:
   - Upload files from local machine
   - Connect to Git repository
   - Use Cloud Source Repositories
4. Upload/select the `app/launchpad` directory
5. The Console will:
   - Create staging bucket automatically
   - Handle all permissions
   - Deploy the application

**Required Permissions**: User needs `App Engine Admin` or `Editor` role

### Method 2: gcloud CLI (After Bucket Exists)

**Prerequisites**: 
- Staging bucket must already exist
- User/service account has required roles

**Command**:
```bash
cd app/launchpad
gcloud app deploy app.yaml
```

**Required Permissions**:
- `roles/appengine.appAdmin`
- `roles/storage.admin`

### Method 3: Cloud Build

**Configuration**: `cloudbuild.yaml` is already created

**Command**:
```bash
gcloud builds submit --config=cloudbuild.yaml .
```

**Required Permissions**:
- Cloud Build service account needs `App Engine Admin` and `Storage Admin`
- Default Cloud Build service account: `464251598887@cloudbuild.gserviceaccount.com`

## Granting Permissions

### Grant Roles to User Account

```bash
# Grant App Engine Admin
gcloud projects add-iam-policy-binding smartq-backend-784299 \
  --member="user:EMAIL@example.com" \
  --role="roles/appengine.appAdmin"

# Grant Storage Admin
gcloud projects add-iam-policy-binding smartq-backend-784299 \
  --member="user:EMAIL@example.com" \
  --role="roles/storage.admin"
```

### Grant Roles to Service Account

```bash
# Grant App Engine Admin
gcloud projects add-iam-policy-binding smartq-backend-784299 \
  --member="serviceAccount:SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com" \
  --role="roles/appengine.appAdmin"

# Grant Storage Admin
gcloud projects add-iam-policy-binding smartq-backend-784299 \
  --member="serviceAccount:SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

### Enable Required APIs

```bash
gcloud services enable appengine.googleapis.com \
  storage-component.googleapis.com \
  storage-api.googleapis.com \
  cloudbuild.googleapis.com \
  --project=smartq-backend-784299
```

## Current Account Status

### User Account: `shivanshusom@gmail.com`
- ✅ Has `roles/storage.admin`
- ✅ Has `roles/owner` (includes all permissions)
- ❌ Cannot create staging bucket via CLI (domain verification issue)

### Service Account: `launchpad@smartq-backend-784299.iam.gserviceaccount.com`
- ✅ Has `roles/owner` (includes all permissions)
- ❌ Cannot create staging bucket via CLI (domain verification issue)

## Troubleshooting

### Error: "staging bucket does not exist"

**Cause**: The staging bucket hasn't been created yet

**Solutions**:
1. Use GCP Console for first deployment (recommended)
2. Manually create bucket via Console Storage browser
3. Contact GCP support if domain verification is blocking creation

### Error: "Access Denied" or "Permission Denied"

**Cause**: Insufficient IAM roles

**Solution**: Grant required roles using commands above

### Error: "API not enabled"

**Cause**: Required GCP API is not enabled

**Solution**: Enable APIs using `gcloud services enable` command

## Firebase Permissions (If Applicable)

If using Firebase services alongside App Engine:

### Required Firebase Roles:
1. **Firebase Admin** (`roles/firebase.admin`)
   - Manage Firebase projects and services
   - Required for: Firebase Hosting, Authentication, Firestore

2. **Firebase Authentication Admin** (`roles/firebaseauth.admin`)
   - Manage Firebase Authentication
   - Required for: User management, OAuth configuration

### Current Firebase Service Accounts:
- `firebase-adminsdk-fbsvc@smartq-backend-784299.iam.gserviceaccount.com`
  - Has `roles/firebase.admin`
  - Has `roles/firebaseauth.admin`

## Best Practices

1. **Use Least Privilege**: Grant only necessary roles
2. **Service Accounts**: Use service accounts for automated deployments
3. **First Deployment**: Always use GCP Console for first deployment
4. **Monitor Permissions**: Regularly audit IAM policies
5. **Document Changes**: Keep track of permission changes

## Quick Reference

### Check Current Permissions
```bash
# List IAM policy for project
gcloud projects get-iam-policy smartq-backend-784299

# Check specific user/service account
gcloud projects get-iam-policy smartq-backend-784299 \
  --flatten="bindings[].members" \
  --filter="bindings.members:EMAIL@example.com"
```

### Verify APIs Enabled
```bash
gcloud services list --enabled --project=smartq-backend-784299
```

### Check App Engine Status
```bash
gcloud app describe --project=smartq-backend-784299
```

## Support Resources

- **GCP Console**: https://console.cloud.google.com/appengine?project=smartq-backend-784299
- **IAM Documentation**: https://cloud.google.com/iam/docs
- **App Engine Docs**: https://cloud.google.com/appengine/docs
- **Storage Docs**: https://cloud.google.com/storage/docs

## Summary

**For successful deployment, you need**:
1. ✅ App Engine Admin API enabled
2. ✅ Storage APIs enabled  
3. ✅ User/Service Account with `App Engine Admin` and `Storage Admin` roles
4. ❌ Staging bucket created (must use Console for first time)

**Recommended Action**: Use GCP Console for deployment to automatically handle bucket creation.

