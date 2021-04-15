#!/bin/bash

# Convert source file of jpylyzer documentation (markdown) to delivery formats:
#
# 1. userManual.html - add this to root of jpylyzer website (includes Jekyll headers)
# 2. Self-contained HTML file for offline use (replaces PDF)
#
# Requires Pandoc and xmllint

# Base name
baseName=jpylyzerUserManual

# Source file
mdSource=$baseName.md

# Style sheet
styleSheet=jpylyzer.css

# Delivery formats

# Website
outWeb=userManual.html

# Self-contained HTML
outHtmlSC=${baseName}.html

# Create file that replaces userManual page on website

# Step 1: convert to HTML
pandoc -s --columns 1000 --toc --toc-depth=2 --ascii -c $styleSheet -w html5 -o tmp.html $mdSource

# Step 2: generate file with Jekyll headers

echo "---" > $outWeb
echo "layout: page" >> $outWeb
echo "title: User Manual" >> $outWeb
echo "---" >> $outWeb
echo "{% include JB/setup %}" >> $outWeb

# Step 3: extract everything inside body element of HTML and add to output file
# This results in a flood of xmllint error messages, but they can be ignored.
xmllint --html --htmlout --xpath "//body/node()" tmp.html >> $outWeb

# Create self-contained HTML file (mainly useful for offline use; replaces PDF)
pandoc -s --columns 1000 --toc --toc-depth=2 --ascii -c $styleSheet -w html5 --self-contained -o $outHtmlSC $mdSource

# Clean-up
rm tmp.html
