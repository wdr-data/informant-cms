from .views import reports, genres, topics, tags, faqs

urlpatterns = []
urlpatterns += reports.urlpatterns
urlpatterns += genres.urlpatterns
urlpatterns += topics.urlpatterns
urlpatterns += tags.urlpatterns
urlpatterns += faqs.urlpatterns
