from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Recipe, Comment
from . import forms
from .forms import CommentForm, RecipeForm


@login_required
def add_recipe(request):
    recipe_form = RecipeForm()
    if request.method == "POST":
        recipe_form = RecipeForm(request.POST, request.FILES)
        if recipe_form.is_valid():
            recipe_form = recipe_form.save(commit=False)
            recipe_form.title = recipe_form.title.title()
            recipe_form.id_user = request.user
            recipe_form.status_recipe = 1
            recipe_form.save()
            return redirect('home')

    return render(request, 'add_recipe.html', context={'recipe_form': recipe_form})


class RecipeList(generic.ListView):
    model = Recipe
    queryset = Recipe.objects.filter(status_recipe=1).order_by('-created_date')
    template_name = 'index.html'
    paginate_by = 6

    

class PostDetail(View):
    def get(self, request, slug, *args, **kwargs):
        queryset = Recipe.objects.filter(status_recipe=1)
        post = get_object_or_404(queryset, slug=slug)
        print(post.slug)        
        comments = post.comments.filter(approved=True).order_by('-created_date') 
        liked = False
        if post.likes.filter(id=self.request.user.id).exists(): 
            liked = True
                    
        return render(
            request,
            'post_detail.html',
            {
                "post": post,
                "slug": post.slug,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )
        
        
    def post(self, request, slug, *args, **kwargs):
        queryset = Recipe.objects.filter(status_recipe=1)
        recipe = get_object_or_404(Recipe, slug=slug)  
        post = get_object_or_404(queryset, slug=slug)               
        comments = post.comments.filter(approved=True).order_by('-created_date') 
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username  
            comment = comment_form.save(commit=False)
            comment.id_recipe = recipe
            comment.save()      
        else:        
            comment_form = CommentForm()

        return render(
            request,
            'post_detail.html',
            {
                "post": post,
                "slug": post.slug,
                "comments": comments,
                "commented": True,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

        
class PostLike(View):
    def post(self, request, slug):
        recipe = get_object_or_404(Recipe, slug=slug)

        if recipe.likes.filter(id=request.user.id).exists():
            recipe.likes.remove(request.user)
        else:
            recipe.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))
        
        
class RecipeEditView(UpdateView):    
    """
    Edit recipe
    """
    model = Recipe
    form_class = RecipeForm
    template_name_suffix = '_update_form'
    template_name = 'edit_recipe.html'
    success_url = '/'

    def get_context_data(self, *args, **kwargs):
        context = super(RecipeEditView, self).get_context_data(*args, **kwargs)
        post = self.get_object()
        context['post'] = post
        return context

class RecipeDeleteView(DeleteView):
    """
    Delete Recipe
    """
    model = Recipe
    template_name = 'delete_recipe.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *args, **kwargs):
        context = super(RecipeDeleteView, self).get_context_data(*args, **kwargs)
        post = self.get_object()
        context['post'] = post
        return context

def about(request):
    """
    About page
    """
    return render(request, 'about.html')

def contact(request):
    """
    Contact page
    """
    return render(request, 'contact.html')

class RecipeDeleteComment(DeleteView):
    """
    Delete comment
    """
    model = Comment
    template_name = 'delete_comment.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *args, **kwargs):
        context = super(RecipeDeleteComment, self).get_context_data(*args, **kwargs)
        post = self.get_object()
        context['post'] = post
        return context
