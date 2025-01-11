import time
import requests
import os
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

console = Console()

# Clear console and display header
def display_header():
    os.system("cls" if os.name == "nt" else "clear")
    header_panel = Panel(
        "Dexter Automation Tool",
        title="Automation Tool",
        subtitle="Mine $SSLX and Collect Gold Eagle Coins!",
        border_style="bold white",
        padding=(1, 2),
        width=50
    )
    console.print(header_panel, justify="center")

# Modify the token input process to include names
def get_token_input():
    token_count = int(console.input("[bold cyan]Enter the number of Bearer tokens: [/bold cyan]"))
    tokens = []
    token_names = []
    for i in range(token_count):
        token_name = console.input(f"[bold green]Enter name for token {i+1}: [/bold green]")
        token_value = console.input(f"[bold green]Enter Bearer token {i+1}: [/bold green]")
        tokens.append(token_value)
        token_names.append(token_name)
    return tokens, token_names

# Create progress table
def create_progress_table(progress_data_list, initial_coins_list, token_names):
    table = Table(border_style="bold blue")
    table.add_column("Token Name", style="cyan", justify="center")
    table.add_column("Initial Coins", style="green", justify="center")
    table.add_column("Old Coins", style="yellow", justify="center")
    table.add_column("New Coins", style="green", justify="center")
    table.add_column("Current Energy", style="cyan", justify="center")
    table.add_column("Incomplete Tasks", style="yellow", justify="center")
    table.add_column("Unregistered Events", style="red", justify="center")

    for index, (progress_data, initial_coins) in enumerate(zip(progress_data_list, initial_coins_list)):
        if progress_data:
            old_coins = progress_data.get("old_coins", 0)
            new_coins = progress_data.get("coins_amount", 0)
            table.add_row(
                token_names[index],
                str(initial_coins),
                str(old_coins),
                str(new_coins),
                f"{progress_data['energy']}/{progress_data['max_energy']}",
                str(progress_data['not_completed_tasks_count']),
                str(progress_data['not_registerd_events_count']),
            )
        else:
            table.add_row(token_names[index], "Error", "Error", "Error", "Error", "Error", "Error")
    return table

# Fetch progress data
def get_progress_data(headers):
    try:
        response = requests.get("https://gold-eagle-api.fly.dev/user/me/progress", headers=headers)
        print(f"Response Status: {response.status_code}")  # Debugging line
        if response.status_code == 200:
            progress_data = response.json()
            print(f"Progress Data: {progress_data}")  # Debugging line
            return progress_data
        else:
            console.print(f"❌ Failed to fetch progress data: {response.status_code}", style="bold red")
            return None
    except Exception as e:
        console.print(f"❌ Error fetching progress data: {e}", style="bold red")
        return None

# Collect coins if enough energy is available
def collect_coins(headers, energy):
    if energy > 0:
        timestamp = int(time.time())
        salt = str(random.randint(1000, 9999))
        body = {"available_taps": energy, "count": energy, "timestamp": timestamp, "salt": salt}
        try:
            response = requests.post("https://gold-eagle-api.fly.dev/tap", json=body, headers=headers)
            if response.status_code == 200:
                data = response.json()
                console.print(f"✅ Collected coins! Total coins: {data.get('coins_amount', 0)}", style="bold green")
            else:
                console.print(f"❌ Failed to collect coins: {response.status_code}", style="bold red")
        except Exception as e:
            console.print(f"❌ Error collecting coins: {e}", style="bold red")
    else:
        console.print("⚠️ Not enough energy to collect coins.", style="bold yellow")

# Handle user input during `Ctrl+C`
def handle_interrupt(tokens, token_names, interval_seconds, random_interval_enabled):
    while True:
        console.print("\n[bold cyan]Choose an option:[/bold cyan]")
        console.print("[1] Pause script")
        console.print("[2] Close script")
        console.print("[3] Add new token")
        console.print("[4] Remove a token")
        console.print("[5] Change collection interval")
        console.print("[6] Enable/Disable random interval (1-5 minutes)")

        choice = console.input("[bold green]Enter your choice: [/bold green]")

        if choice == "1":
            console.print("[yellow]Script paused. Press Enter to continue...[/yellow]")
            input()
            return tokens, token_names, interval_seconds, random_interval_enabled
        elif choice == "2":
            console.print("[red]Closing script. Goodbye![/red]")
            exit(0)
        elif choice == "3":
            new_token_name = console.input("[bold green]Enter the name for the new token: [/bold green]")
            new_token = console.input("[bold green]Enter the new token: [/bold green]")
            tokens.append(new_token)
            token_names.append(new_token_name)
            console.print("[green]New token added successfully![/green]")
            return tokens, token_names, interval_seconds, random_interval_enabled
        elif choice == "4":
            for i, token_name in enumerate(token_names, 1):
                console.print(f"[{i}] {token_name} - {tokens[i-1]}")
            remove_index = console.input("[bold red]Enter the number of the token to remove: [/bold red]")
            try:
                remove_index = int(remove_index) - 1
                removed_token_name = token_names.pop(remove_index)
                removed_token = tokens.pop(remove_index)
                console.print(f"[red]Removed token: {removed_token_name} - {removed_token}[/red]")
                return tokens, token_names, interval_seconds, random_interval_enabled
            except (ValueError, IndexError):
                console.print("[red]Invalid selection. Try again.[/red]")
        elif choice == "5":
            new_interval = console.input("[bold green]Enter the new collection interval (in seconds): [/bold green]")
            try:
                interval_seconds = int(new_interval)
                random_interval_enabled = False
                console.print(f"[green]Collection interval set to {interval_seconds} seconds.[/green]")
                return tokens, token_names, interval_seconds, random_interval_enabled
            except ValueError:
                console.print("[red]Invalid input. Please enter a valid number.[/red]")
        elif choice == "6":
            random_interval_enabled = not random_interval_enabled
            status = "enabled" if random_interval_enabled else "disabled"
            console.print(f"[green]Random interval {status}.[/green]")
            return tokens, token_names, interval_seconds, random_interval_enabled
        else:
            console.print("[red]Invalid choice. Please select a valid option.[/red]")

# Main function to process multiple tokens periodically
def process_tokens_periodically(tokens, token_names, interval_seconds=60, random_interval_enabled=False):
    headers_list = [{"authorization": f"Bearer {token}"} for token in tokens]
    initial_coins_list = []
    progress_data_list = [{} for _ in tokens]

    # Fetch initial coins
    for headers in headers_list:
        progress_data = get_progress_data(headers)
        if progress_data:
            initial_coins = progress_data.get("coins_amount", 0)
            initial_coins_list.append(initial_coins)
            print(f"Initial Coins: {initial_coins}")  # Debugging line
        else:
            initial_coins_list.append(0)

    try:
        with Live(console=console, refresh_per_second=10) as live:
            while True:
                # Update progress data
                for i, headers in enumerate(headers_list):
                    progress_data = get_progress_data(headers)
                    if progress_data:
                        progress_data["old_coins"] = progress_data_list[i].get("coins_amount", 0)
                        progress_data_list[i] = progress_data
                        # Debugging line for coins and energy
                        print(f"Token: {token_names[i]} - Coins: {progress_data.get('coins_amount', 0)} - Energy: {progress_data.get('energy', 0)}")

                        # Collect coins if enough energy is available
                        collect_coins(headers, progress_data['energy'])

                # Update interval if random interval is enabled
                if random_interval_enabled:
                    interval_seconds = random.randint(60, 300)

                # Clear screen and display updated headers and table
                os.system("cls" if os.name == "nt" else "clear")
                display_header()

                # Display table and countdown timer
                for seconds_left in range(interval_seconds, 0, -1):
                    table = create_progress_table(progress_data_list, initial_coins_list, token_names)
                    countdown_text = f"Next update in: {seconds_left} seconds"
                    live.update(
                        Panel(
                            table,
                            title="📊 Progress Data",
                            subtitle=countdown_text,
                            border_style="bold green",
                        )
                    )
                    time.sleep(1)

    except KeyboardInterrupt:
        tokens, token_names, interval_seconds, random_interval_enabled = handle_interrupt(tokens, token_names, interval_seconds, random_interval_enabled)
        process_tokens_periodically(tokens, token_names, interval_seconds, random_interval_enabled)

# Main execution
if __name__ == "__main__":
    display_header()
    try:
        tokens, token_names = get_token_input()
        console.print("\n🔄 Starting periodic execution...\n", style="bold green")
        process_tokens_periodically(tokens, token_names)
    except ValueError:
        console.print("❌ Invalid input. Please enter valid tokens.", style="bold red")
