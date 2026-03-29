#!/usr/bin/env bash

# Paths are strictly limited to .config directories
REPO_CONFIG="/home/leo/Documents/my-hyprland-dots/dots/.config"
ACTUAL_CONFIG="/home/leo/.config"

echo "Syncing matching folders from $ACTUAL_CONFIG to $REPO_CONFIG..."

# Loop through every folder currently in the repo's .config directory
for folder_path in "$REPO_CONFIG"/*/; do
    # Get the folder name (e.g., 'hypr')
    folder_name=$(basename "$folder_path")
    
    # Only sync if this exact folder name exists in your actual ~/.config
    if [ -d "$ACTUAL_CONFIG/$folder_name" ]; then
        echo "Updating: $folder_name"
        
        # Sync the content from ~/.config to the repo
        # --delete ensures the repo matches your active config exactly
        # --exclude='Cache*' prevents pulling in temporary/garbage files
        rsync -av --delete \
            --exclude='Cache*' \
            --exclude='cache*' \
            --exclude='.git' \
            "$ACTUAL_CONFIG/$folder_name/" "$REPO_CONFIG/$folder_name/"
    fi
done

# Sync loose files that are in both .config locations
find "$REPO_CONFIG" -maxdepth 1 -type f | while read -r file; do
    filename=$(basename "$file")
    if [ -f "$ACTUAL_CONFIG/$filename" ]; then
        echo "Updating file: $filename"
        cp "$ACTUAL_CONFIG/$filename" "$file"
    fi
done

echo "Sync complete."

# Versioning and Git logic
VERSION_FILE="$ACTUAL_CONFIG/illogical-impulse/version"

if git diff --quiet && git diff --cached --quiet; then
    echo "No changes to commit in the repository."
else
    echo "Changes detected."
    git add .
    
    # Ask for commit message
    default_msg="sync: update configs from local PC ($(date +%Y-%m-%d))"
    echo "Enter commit message (Leave empty for default: '$default_msg'):"
    read -r user_msg
    
    commit_msg="${user_msg:-$default_msg}"
    
    if git commit -m "$commit_msg"; then
        # If push is successful, update the local version signature
        if git push; then
            echo "Push successful. Updating version signature..."
            git rev-parse HEAD > "$VERSION_FILE"
        else
            echo "Push failed. You may need to manual pull/merge."
        fi
    else
        echo "Commit failed."
    fi
fi

echo "Only matching folders within .config were touched."
