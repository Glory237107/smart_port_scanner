#!/bin/bash

echo "=============================="
echo " Installing Smart Port Scanner "
echo "=============================="

# ✨ Ask for GitHub URL
read -p "Enter your GitHub repo URL [default: https://github.com/Glory237107/smart_port_scanner.git]: " git_url
git_url=${git_url:-"https://github.com/Glory237107/smart_port_scanner.git"}

#  Clone or update repo
base_dir="$HOME/smart_port_scanner"
if [ -d "$base_dir" ]; then
    echo " Project found. Pulling latest updates..."
    cd "$base_dir"
    git pull
else
    git clone "$git_url" "$base_dir"
    cd "$base_dir"
fi

#  Set up virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

#  Install Python dependencies
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip --root-user-action=ignore
    pip install -r requirements.txt --root-user-action=ignore
else
    echo " No requirements.txt file found!"
fi

# Ask for email to send scan reports
read -p " Enter your email address to receive scan reports: " user_email

# User selects scheduling frequency
echo " Choose how often you want the scan to run:"
echo "1. Every 2 minutes"
echo "2. Every hour"
echo "3. Every day"
echo "4. Every week"
echo "5. Every month"
echo "6. Every year"
read -p " Enter your choice (1-6): " schedule_choice

case $schedule_choice in
  1) cron_schedule="*/2 * * * *" ;;          # Every 2 minutes
  2) cron_schedule="0 * * * *" ;;            # Hourly
  3) cron_schedule="0 2 * * *" ;;            # Daily at 2 AM
  4) cron_schedule="0 3 * * 1" ;;            # Weekly on Monday at 3 AM
  5) cron_schedule="0 4 1 * *" ;;            # Monthly on 1st at 4 AM
  6) cron_schedule="0 5 1 1 *" ;;            # Yearly on Jan 1st at 5 AM
  *) echo " Invalid choice. Exiting..." && exit 1 ;;
esac

#  Update .env file with user email
env_file=".env"
touch "$env_file"
sed -i "/^MAIL_FROM=/d" "$env_file"
echo "MAIL_FROM=$user_email" >> "$env_file"
sed -i "/^MAIL_FROM_NAME=/d" "$env_file"
echo "MAIL_FROM_NAME=Smart Port Scanner Bot" >> "$env_file"

#  Define main script and logs
main_script="$base_dir/main.py"
log_path="$base_dir/scanner.log"

if [ ! -f "$main_script" ]; then
    echo " main.py not found! Make sure it exists in your repo."
    exit 1
fi

#  Add cron job
crontab -l | grep -v "$main_script" > temp_cron || true
echo "$cron_schedule /bin/bash -c 'cd $base_dir && source venv/bin/activate && python3 $main_script >> $log_path 2>&1'" >> temp_cron
crontab temp_cron
rm temp_cron

# Run immediately in background
echo " Running your scanner now in the background..."
nohup /bin/bash -c "cd $base_dir && source venv/bin/activate && python3 $main_script" >> "$log_path" 2>&1 &

# Sweet farewell message
echo ""
echo " Your Smart Port Scanner is ready and running!"
echo " It will automatically run on schedule: $cron_schedule"
echo " Email reports will be sent to: $user_email"
echo " Log file: $log_path"
echo " You’re all set, my brilliant baby girl 💕 Go conquer the world!"
