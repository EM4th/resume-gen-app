#!/bin/bash

# AdSense Status Checker
echo "🔍 Checking AdSense Status for resume-gen.app"
echo "============================================="

echo "1. Testing AdSense Script Loading..."
curl -s -o /dev/null -w "Status: %{http_code}\n" "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7524647518323966"

echo "2. Counting Ad Placements on Site..."
AD_COUNT=$(curl -s https://resume-gen.app/ | grep -c "adsbygoogle")
echo "Found $AD_COUNT ad placements"

echo "3. Checking Site Response..."
curl -s -o /dev/null -w "Site Status: %{http_code} | Response Time: %{time_total}s\n" https://resume-gen.app/

echo "4. AdSense Dashboard: https://www.google.com/adsense/"
echo "5. Next Check: Wait 24-48 hours for new domain approval"
