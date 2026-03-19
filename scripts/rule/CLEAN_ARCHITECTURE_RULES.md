# Pubstar iOS SDK – Internal Development Environment Setup Guide

This document is intended for internal developers to help them:

- Clone and set up the Pubstar iOS SDK repository

- Run the AddSDK test application

- Enable / disable Prebid Native testing

- Build the SDK into a distributable .xcframework

The structure and tone of this document follow the public README layout to keep internal and external documentation consistent.

## 1. Environment Requirements

Before starting, make sure your local machine has the following installed:

- macOS

- Xcode (latest stable version recommended)

- CocoaPods

- Ruby + Bundler (required for Fastlane)

- Firebase CLI (mandatory for Firebase authentication scripts)

- Access to the internal GitHub repository

⚠️ The project uses CocoaPods, so always open the project via the .xcworkspace file.

## 2. SDK Project Structure

The core SDK source code is located inside the `Pubstar/` directory.

High-level structure

```text
Pubstar/
├── AdapterGoogle/
├── AdapterOrtb/
├── AdapterPrebid/
├── AdapterPubStar/
├── AdapterAppLovin/
├── core/
└── layouts/
```

Directory responsibilities

| Directory          | Description                                                                          |
| ------------------ | ------------------------------------------------------------------------------------ |
| `core/`            | Core SDK logic, public APIs, managers, utilities, and shared components              |
| `AdapterGoogle/`   | Google Ads adapter implementation                                                    |
| `AdapterOrtb/`     | OpenRTB adapter implementation                                                       |
| `AdapterPrebid/`   | Prebid adapter and Prebid-specific integrations                                      |
| `AdapterPubStar/`  | Internal Pubstar adapter logic                                                       |
| `AdapterAppLovin/` | AppLovin adapter integration                                                         |
| `layouts/`         | UI layouts, views, and templates used for ad rendering (e.g. Banner Ads, Native Ads) |

## 3. Enable / Disable Prebid Native Mode

The SDK supports switching between **Prebid Native mode** and **standard Prebid mode** using a single flag.

Configuration

```swift
// Pubstar/core/LogUtils.swift

public class LogUtils {
    public static let isNativePrebidTest = false
}
```

Behavior

| Value   | Result                                |
| ------- | ------------------------------------- |
| `false` | Use **standard Prebid** flow          |
| `true`  | Enable **Prebid Native** testing mode |

⚠️ Make sure to revert this flag to false before commiting, merging or releasing.

## 4. Test Application – AddSDK

The repository includes a sample app named `AddSDK`, used for testing and validating the SDK.

AddSDK project structure

```text
AddSDK/
├── AddSDK/
├── AddSDK.xcodeproj
├── AddSDK.xcworkspace
├── Build/
├── fastlane/
├── Gemfile
├── Gemfile.lock
├── Podfile
├── Podfile.lock
├── Pods/
└── README.md
```

## 5. Fastlane Setup (AddSDK)

The **AddSDK** app is integrated with **Fastlane** for building and automation.

### Fastlane directory structure

```text
fastlane/
├── Appfile
├── Fastfile
├── Matchfile
├── Pluginfile
├── README.md
├── release-notes.txt
├── report.xml
├── setup_fastlane.sh
└── setup_firebase.sh
```
