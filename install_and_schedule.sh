#!/bin/bash

echo "=============================="
echo "  Installing Smart Port Scanner"
echo "=============================="

# Get GitHub URL
read -p " Enter your GitHub repo URL (https://github.com/Glory237107/smart_port_scanner.git): " git_url

#  Clone or pull repo
base_dir="$HOME/smart_port_scanner"
if [ -d "$base_dir" ]; then
    echo " Project exists. Pulling latest changes..."
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

#  Install Python packages
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo " No requirements.txt found!"
fi

#  Ask for email + time schedule
read -p " Enter your email address to receive reports: " user_email
read -p " Enter cron schedule (e.g. '*/2 * * * *' for every 2 minutes): " cron_schedule

#  Update .env file
env_file=".env"
touch "$env_file"
sed -i "/^MAIL_FROM=/d" "$env_file"
echo "MAIL_FROM=$user_email" >> "$env_file"
sed -i "/^MAIL_FROM_NAME=/d" "$env_file"
echo "MAIL_FROM_NAME=Smart Port Scanner Bot" >> "$env_file"

#  Prepare main script
main_script="$base_dir/main.py"
log_path="$base_dir/scanner.log"

if [ ! -f "$main_script" ]; then
    echo " main.py not found! Exiting."
    exit 1
fi

#  Schedule with cron
crontab -l | grep -v "$main_script" > temp_cron || true
echo "$cron_schedule /bin/bash -c 'cd $base_dir && source venv/bin/activate && python3 $main_script >> $log_path 2>&1'" >> temp_cron
crontab temp_cron
rm temp_cron

echo " Cron job scheduled: $cron_schedule"
echo " Email reports will be sent to: $user_email"
echo " Log file: $log_path"

#  Launch immediately in background
echo " Launching now in the background..."
nohup /bin/bash -c "cd $base_dir && source venv/bin/activate && python3 $main_script" >> "$log_path" 2>&1 &

echo " Your scanner is running NOW in the background and will keep running every $cron_schedule!"
echo " You can safely close this terminal. It's fully autonomous now "
