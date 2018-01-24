from .views import reports, genres, topics, tags

urlpatterns = []
urlpatterns += reports.urlpatterns
urlpatterns += genres.urlpatterns
urlpatterns += topics.urlpatterns
urlpatterns += tags.urlpatterns
