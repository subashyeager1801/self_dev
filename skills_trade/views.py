"""
Skills Trade views — Peer skill exchange marketplace and matchmaking.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import SkillTradeListing, TradeRequest


@login_required
def marketplace_view(request):
    """Main peer skill trading marketplace."""
    listings = SkillTradeListing.objects.filter(is_active=True).select_related('user')
    my_listings = listings.filter(user=request.user)
    my_requests = TradeRequest.objects.filter(listing__user=request.user)

    context = {
        'listings': listings,
        'my_listings': my_listings,
        'my_requests': my_requests,
        'show_nav': True,
        'active_nav': 'skills_trade',
    }
    return render(request, 'skills_trade/index.html', context)


@login_required
def create_listing_api(request):
    """Post a new skill trade listing."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    offering = request.POST.get('skill_offering', '').strip()
    seeking = request.POST.get('skill_seeking', '').strip()
    description = request.POST.get('description', '').strip()
    contact = request.POST.get('contact_handle', '').strip()

    if not offering or not seeking:
        return JsonResponse({'error': 'Offering and seeking skills required'}, status=400)

    listing = SkillTradeListing.objects.create(
        user=request.user,
        skill_offering=offering,
        skill_seeking=seeking,
        description=description,
        contact_handle=contact
    )

    return JsonResponse({'status': 'ok', 'id': listing.id})


@login_required
def send_trade_request_api(request):
    """Send a connection request to a listing owner."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    listing_id = request.POST.get('listing_id')
    pitch = request.POST.get('pitch_message', '').strip()

    try:
        listing = SkillTradeListing.objects.get(id=listing_id)
        if listing.user == request.user:
            return JsonResponse({'error': 'Cannot trade with yourself'}, status=400)

        TradeRequest.objects.create(
            listing=listing,
            sender=request.user,
            pitch_message=pitch
        )

        # Notify listing owner
        from notifications.utils import send_in_app_notification
        send_in_app_notification(
            user=listing.user,
            title=f"🤝 New Skill Exchange Request from {request.user.first_name or request.user.username}",
            message=f"Received a connect request on your '{listing.skill_offering}' listing.",
            notification_type='trade',
            action_url='/skills-trade/'
        )

        return JsonResponse({'status': 'ok'})
    except SkillTradeListing.DoesNotExist:
        return JsonResponse({'error': 'Listing not found'}, status=404)
