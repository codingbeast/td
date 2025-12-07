# Automated Trading Bot - Setup Guide

## Overview

This automated trading bot connects to Zerodha's trading platform and provides notifications via Telegram. The bot requires several environment variables to be set up before it can run properly.

## Inspiration

Most of the strategies are based on the guidance of our trading Guruji, **Mahesh Sir**, and some strategies have been created by me.

Mahesh Chander Kaushik : [Mahesh Chander Kaushik](https://www.youtube.com/@Maheshchanderkaushik)  
Raj kumar Rao : [CodingBeast](https://www.youtube.com/@codingbeast)
## Prerequisites

- GitHub account
- Zerodha trading account credentials
- Telegram bot token and user ID
- Google Service Account credentials (if using Google drive integration for log files)

## Setup Instructions

### 1. Environment Variables Configuration

Add these secrets to your GitHub repository:

1. Go to your repository's **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret** for each required variable:

#### Required Secrets

| Secret Name                     | Description                                                                   |
| ------------------------------- | ----------------------------------------------------------------------------- |
| `TELEGRAM_BOT_TOKEN`            | Obtain from Telegram's @BotFather bot                                         |
| `TELEGRAM_USER_ID`              | Get from @userinfobot on Telegram                                             |
| `ZERODHA_USER_ID`               | Your Zerodha Kite login ID                                                    |
| `ZERODHA_USER_PASSWORD`         | Your Zerodha Kite login password                                              |
| `ZERODHA_TPIN_TOKEN`            | Zerodha two-factor authentication token                                       |
| `GOOGLE_SERVICE_ACCOUNT_BASE64` | Base64 encoded Google Service Account JSON(service_account_encoder.py --help) |

### 2. Automation Setup

Once all secrets are configured:

1. The GitHub Actions workflow will automatically use these environment variables
2. The bot will run according to the schedule defined in `.github/workflows/`
3. You'll receive status notifications via Telegram

### How to stop some strategies  
goto .github\workflows\[open your strategy file that you want to stop]  
here are similar schedule codes in each file you have to simply add # before the cron (word)  
for example this will run 
```on:
  schedule:
    # Single trigger at 8:00 AM IST (2:30 AM UTC)
    - cron: '30 0 1 * 1-5'  # Runs Mon-Fri at 8:00 AM IST
  workflow_dispatch:  # Manual trigger for both buy and sell
```  
this will not run becouse we disabled the cron (so if you want to run this you have to manually trigger this)   
```on:
  schedule:
    # Single trigger at 8:00 AM IST (2:30 AM UTC)
    #- cron: '30 0 1 * 1-5'  # Runs Mon-Fri at 8:00 AM IST
  workflow_dispatch:  # Manual trigger for both buy and sell
```

### Troubleshooting

- Double-check all secret names are exactly as shown above
- Ensure there are no trailing spaces in secret values
- For Google credentials, make sure to base64 encode the entire JSON file

## 🎯 Algorithm Overview

**Automated trading bots for GoldBEES and CPSE ETFs with 3% profit targets**
*Built with Python using Zerodha's Kite API | Telegram notifications | Google Drive logging*

---

### 🟡 GoldBEES Algorithm

- **Target**: 2% profit (configurable)
- **Strategy**:
  - Buys at 0.30% below current price (manually set inside config)
  - Sells at 2% above average purchase price
  - Minimum sell quantity: 20 units

### 🔵 Lahari Algorithm

- **Target**: 3% profit
- **Strategy**:
  - Uses 15-day moving average to determine uptrend/downtrend
  - Adjusts buy levels based on market direction
  - Implements flag-based position management
### 🟡 Hommagenius Algorithm
- **Target**: 3% profit
- **Strategy**:
  - only run at nifty expiry day at aprox 3:00 PM
  - check if closing price is lower then or not from old week
  - buy if candle is not bull.
---
##  🙏 Support My Work
If you find this project helpful and would like to support its development, consider buying me a coffee or making a small donation.  
### 📱 UPI / QR Code  
You can scan the QR code below or use the UPI ID directly to donate:  
<img src="td/tests/integration/donation_qr.jpeg" alt="Donate via UPI" width="200" />

UPI ID: raj0kumar00@oksbi   

    Every contribution, big or small, helps me keep building and sharing more open-source tools. Thank you, for your support!

## ❤️ Sponsors / Hire Me

This project is maintained in my personal time.  
If you want **priority support**, **custom improvements**, or **dedicated development**,  
you can sponsor or hire me.

### 🛠 Hire me for custom work  
I build:

✔ Automated trading bots  
✔ Web Scraping  
✔ Automating boring stuff  
✔ Backtesting automation  
✔ Website and App Development  
✔ Social media pages management  

**Email:** advrter@gmail.com  
**Telegram:** @anistdev  


# ⚠️ Warning & Liability Disclaimer

> **IMPORTANT — READ BEFORE USING THIS SOFTWARE**
>
> This automated trading bot may place real orders in your brokerage account.  
> By using this software, you agree to the following:
>
> - **I (the developer) am NOT responsible** for any kind of loss — financial, technical, data-related, or otherwise.
> - This bot is provided **for educational purposes only** and does **NOT** constitute financial advice.
> - You are fully and solely responsible for:
>   - All trading decisions  
>   - All executed orders  
>   - Your money and your account  
>   - API key security  
>   - Compliance with broker rules & local laws  
> - There is **NO WARRANTY** of any kind — including but not limited to:
>   - Accuracy  
>   - Reliability  
>   - Profitability  
>   - Uptime  
>   - Error-free operation  
>
> **Use this software entirely at your own risk.**  
> By continuing, you accept 100% responsibility for all outcomes — good or bad.

## ⚠️ Disclaimer

**THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.** By using this automated trading bot, you agree to the following:

1. **Financial Risk**: Trading involves substantial risk of loss and is not suitable for every investor. Past performance is not indicative of future results.
2. **No Guarantees**: There are no guarantees of profit or freedom from loss. You assume all financial risk.
3. **Testing Required**: Always test with virtual/simulated accounts before live trading.
4. **Compliance**: You are solely responsible for ensuring compliance with:

   - Your broker's terms of service
   - Local financial regulations
   - Exchange rules
5. **Monitoring Required**: Do not leave the bot unattended. Technical failures can result in significant losses.
6. **Liability**: The developers accept no liability for:

   - Trading losses
   - Technical failures
   - Security breaches
   - Account restrictions/bans
7. **Security**: API keys and credentials are used at your own risk. Never share these with untrusted parties.

*By using this software, you acknowledge that you understand these risks and accept full responsibility for all trading decisions and outcomes.*
