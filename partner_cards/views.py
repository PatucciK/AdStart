# partner_cards/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import PartnerCard
from .forms import PartnerCardForm


@login_required
def edit_partner_card(request):
    try:
        partner_card = PartnerCard.objects.get(advertiser=request.user.advertiser)
    except PartnerCard.DoesNotExist:
        partner_card = None

    if request.method == 'POST':
        form = PartnerCardForm(request.POST, request.FILES, instance=partner_card)
        if form.is_valid():
            partner_card = form.save(commit=False)
            partner_card.advertiser = request.user.advertiser
            partner_card.save()
            return redirect('view_partner_card')
    else:
        form = PartnerCardForm(instance=partner_card)

    return render(request, 'partner_cards/edit_partner_card.html', {'form': form})


@login_required
def view_partner_card(request):
    partner_card = PartnerCard.objects.get(advertiser=request.user.advertiser)
    return render(request, 'partner_cards/view_partner_card.html', {'partner_card': partner_card})
