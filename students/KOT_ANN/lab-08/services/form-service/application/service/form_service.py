from application.port.out.form_schema_repository import FormSchemaRepository
from application.command.create_form_command import CreateFormCommand
from application.query.get_form_query import GetFormQuery
from domain.models.form import Form, FormField, AntiSpamSettings


class FormService:
    def __init__(self, repository: FormSchemaRepository):
        self.repository = repository
    
    def create_form(self, command: CreateFormCommand) -> None:
        fields = [
            FormField(name=f["name"], field_type=f["type"], required=f.get("required", False))
            for f in command.fields
        ]
        settings = AntiSpamSettings(
            min_filling_time_sec=command.anti_spam_settings.get("min_filling_time_sec", 30),
            min_comment_length=command.anti_spam_settings.get("min_comment_length", 3),
            block_repeating_chars=command.anti_spam_settings.get("block_repeating_chars", True)
        )
        form = Form(form_id=command.form_id, fields=fields, anti_spam_settings=settings)
        self.repository.save(form)
    
    def get_form(self, query: GetFormQuery) -> dict:
        form = self.repository.find_by_id(query.form_id)
        if not form:
            return None
        return {
            "form_id": form.form_id,
            "fields": [{"name": f.name, "type": f.field_type, "required": f.required} for f in form.fields],
            "anti_spam_settings": {
                "min_filling_time_sec": form.anti_spam_settings.min_filling_time_sec,
                "min_comment_length": form.anti_spam_settings.min_comment_length,
                "block_repeating_chars": form.anti_spam_settings.block_repeating_chars
            }
        }