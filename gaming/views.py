import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from .models import Wallet

@login_required
def gaming_home(request):
    # Safely ensure the user has a wallet when visiting the home page
    Wallet.objects.get_or_create(user=request.user, defaults={'electis_balance': 50})
    return render(request, 'gaming/home.html')

@login_required
def arcade_coin_flip(request):
    # Auto-creates wallet if missing
    wallet, created = Wallet.objects.get_or_create(user=request.user, defaults={'electis_balance': 50})

    if request.method == 'POST':
        try:
            bet = int(request.POST.get('bet', 50))
        except ValueError:
            messages.error(request, "Invalid bet amount entered.")
            return redirect('arcade')

        if bet <= 0:
            messages.error(request, "You must bet at least 1 ⚡!")
            return redirect('arcade')

        if wallet.electis_balance >= bet:
            with transaction.atomic():
                # Re-fetch with row locking for absolute safety
                wallet = Wallet.objects.select_for_update().get(user=request.user)
                if random.choice([True, False]):
                    wallet.electis_balance += bet
                    messages.success(request, f"Victory! You won {bet} ⚡!")
                else:
                    wallet.electis_balance -= bet
                    messages.error(request, f"Defeat! You lost {bet} ⚡.")
                wallet.save()
        else:
            messages.error(request, "You don't have enough Electis for that bet!")

        return redirect('arcade')

    return render(request, 'gaming/arcade.html', {'balance': wallet.electis_balance})

@login_required
def transfer_electis(request):
    # Auto-creates wallet if missing
    sender_wallet, created = Wallet.objects.get_or_create(user=request.user, defaults={'electis_balance': 50})

    if request.method == 'POST':
        target_username = request.POST.get('username', '').strip()

        try:
            amount = int(request.POST.get('amount', 0))
        except ValueError:
            messages.error(request, "Please enter a valid whole number for the amount.")
            return redirect('transfer')

        # Rule 1: Prevent transferring negative amounts or 0
        if amount <= 0:
            messages.error(request, "Transfer amount must be greater than 0 ⚡.")
            return redirect('transfer')

        # Rule 2: Check if the recipient actually exists
        try:
            target_user = User.objects.get(username=target_username)
        except User.DoesNotExist:
            messages.error(request, f"User '{target_username}' does not exist!")
            return redirect('transfer')

        # Rule 3: Prevent transferring money to yourself
        if target_user == request.user:
            messages.error(request, "You cannot transfer Electis to yourself!")
            return redirect('transfer')

        # Rule 4: Ensure recipient has a wallet too (just in case they are an old account)
        receiver_wallet, created = Wallet.objects.get_or_create(user=target_user, defaults={'electis_balance': 50})

        # Rule 5: Overdraft Protection check
        if sender_wallet.electis_balance < amount:
            messages.error(request, f"Transaction failed! You need {amount} ⚡, but you only have {sender_wallet.electis_balance} ⚡.")
            return redirect('transfer')

        # If all rules pass, execute the locked database transfer
        with transaction.atomic():
            s = Wallet.objects.select_for_update().get(user=request.user)
            r = Wallet.objects.select_for_update().get(user=target_user)

            s.electis_balance -= amount
            r.electis_balance += amount
            s.save()
            r.save()

            messages.success(request, f"Successfully transferred {amount} ⚡ to {target_username}!")

        return redirect('transfer')

    return render(request, 'gaming/transfer.html', {'balance': sender_wallet.electis_balance})