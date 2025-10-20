from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserProfileForm
from .models import UserProfile

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    from jobs.models import JobRecommendation
    from cvs.models import CV

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    # Get current CV and recommendations
    current_cv = CV.objects.filter(user=request.user, is_current=True).first()
    recommendations = []
    print(f"\nDebug profile view: Found current CV: {current_cv.id if current_cv else None}")
    
    if current_cv:
        print("Debug: Looking for recommendations...")
        recommendations = JobRecommendation.objects.filter(
            user=request.user,
            cv_id=current_cv.id
        ).select_related('job').order_by('-match_score')[:10]
        
        print(f"Debug: Found {len(recommendations)} recommendations for CV {current_cv.id}")
        print("Debug: First few recommendations:")
        for rec in recommendations[:3]:
            print(f"- {rec.job.title} (score: {rec.match_score}, skills: {rec.matching_skills})")
            
        # Double check the recommendation exists in database
        total_recs = JobRecommendation.objects.filter(user=request.user).count()
        print(f"Debug: Total recommendations in database for user: {total_recs}")
        
    print(f"Debug: Final context - CV: {bool(current_cv)}, Recommendations: {len(recommendations)}")
    
    context = {
        'form': form,
        'current_cv': current_cv,
        'recommendations': recommendations,
    }
    return render(request, 'accounts/profile.html', context)
