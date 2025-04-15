from django.urls import path
from .views import NoteListCreateView, NoteDeleteView, GetMyOrgUsersView

urlpatterns = [
    path("notes/", NoteListCreateView.as_view(), name="note_list"),
    path("organization/users/", GetMyOrgUsersView.as_view(), name="org_users"),
    path("notes/delete/<int:pk>", NoteDeleteView.as_view(), name="note_delete"),
]
