from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from .models import Voucher, Reward, UserReward, VoucherRedemption, RewardCategory

@login_required
def marketplace(request):
    """Display available rewards and vouchers."""
    # Get available vouchers
    now = timezone.now()
    vouchers = Voucher.objects.filter(
        status='available'
    ).filter(
        models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now)
    )
    
    # Filter out fully used vouchers manually or via complex query if needed
    # For simplicity, we'll iterate or trust the manager, but let's just filter by is_available property in template or simple query
    # Simpler query:
    vouchers = [v for v in vouchers if v.is_available]
    
    # Get reward categories
    categories = RewardCategory.objects.filter(is_active=True).prefetch_related('rewards')
    
    context = {
        'vouchers': vouchers,
        'categories': categories,
    }
    return render(request, 'rewards/marketplace.html', context)

@login_required
def my_rewards(request):
    """Display user's earned rewards and redemption history."""
    # Get earned rewards
    user_rewards = UserReward.objects.filter(
        user=request.user, 
        is_active=True
    ).select_related('reward')
    
    # Get voucher redemptions
    redemptions = VoucherRedemption.objects.filter(
        user=request.user
    ).select_related('voucher')
    
    context = {
        'user_rewards': user_rewards,
        'redemptions': redemptions,
        'user': request.user
    }
    return render(request, 'rewards/my_rewards.html', context)


@login_required
def redeem_voucher(request, voucher_id):
    """Handle voucher redemption."""
    if request.method != 'POST':
        return redirect('rewards:marketplace')
        
    voucher = get_object_or_404(Voucher, id=voucher_id)
    user = request.user
    
    # Validation
    if not voucher.is_available:
        messages.error(request, 'This voucher is no longer available or has expired.')
        return redirect('rewards:marketplace')
        
    if user.coins < voucher.cost_in_coins:
        messages.error(request, 'Insufficient MateCoins balance.')
        return redirect('rewards:marketplace')
        
    # Process redemption
    try:
        # Deduct coins
        user.coins -= voucher.cost_in_coins
        user.save()
        
        # Increment usage
        voucher.current_uses += 1
        voucher.save()
        
        # Create redemption record
        VoucherRedemption.objects.create(
            user=user,
            voucher=voucher,
            coins_spent=voucher.cost_in_coins
        )
        
        # Create UserReward record (treating voucher as a reward for record keeping if needed, 
        # but the model distinguishes them. Let's just stick to VoucherRedemption as per model structure)
        
        messages.success(request, f'Successfully redeemed {voucher.title}! Code: {voucher.code}')
        return redirect('rewards:user_rewards')
        
    except Exception as e:
        messages.error(request, 'An error occurred during redemption.')
        return redirect('rewards:marketplace')
