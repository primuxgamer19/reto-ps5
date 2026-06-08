# widgets/date_edit_popup.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
import datetime

class DateEditPopup(Popup):
    def __init__(self, target="meta", initial_date=None, on_save=None, **kwargs):
        if not initial_date:
            initial_date = datetime.date.today().strftime("%Y-%m-%d")
        
        if target == "meta":
            title_text = 'Editar fecha límite'
            label_text = 'Fecha límite del reto'
        elif target == "salario":
            title_text = 'Editar fecha de salario'
            label_text = 'Fecha de inicio del salario'
        elif target == "regalo":
            title_text = 'Editar fecha del regalo'
            label_text = 'Fecha en la que recibiste la plata'
        else: 
            title_text = 'Editar fecha del pecado'
            label_text = 'Fecha en la que pecaste'

        super().__init__(title=title_text, size_hint=(0.85, 0.6), **kwargs)
        
        self.on_save = on_save
        self.month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        try:
            y, m, d = initial_date.split('-')
            self.current_year = int(y)
            self.current_month = int(m)
            self.current_day = int(d)
        except:
            self.current_year, self.current_month, self.current_day = 2026, 1, 1

        # Guardar target para la nueva lógica de restricciones
        self.target = target

        content = BoxLayout(orientation='vertical', padding=20, spacing=10)

        content.add_widget(Label(
            text=label_text,
            font_size='18sp', bold=True, size_hint_y=None, height=40
        ))

        content.add_widget(Widget()) 

        fields_container = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=100)

        ano_col = BoxLayout(orientation='vertical', spacing=5)
        ano_col.add_widget(Label(text="Año", size_hint_y=None, height=25))
        self.year_input = TextInput(
            text=str(self.current_year), multiline=False, input_filter='int',
            background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),
            size_hint_y=None, height=45, halign='center'
        )
        ano_col.add_widget(self.year_input)

        mes_col = BoxLayout(orientation='vertical', spacing=5)
        mes_col.add_widget(Label(text="Mes", size_hint_y=None, height=25))
        self.month_btn = Button(
            text=self.month_names[self.current_month-1],
            background_normal='', background_color=(1, 1, 1, 1), color=(0, 0, 0, 1),
            size_hint_y=None, height=45
        )
        self.month_btn.bind(on_press=self._open_month_popup)
        mes_col.add_widget(self.month_btn)

        dia_col = BoxLayout(orientation='vertical', spacing=5)
        dia_col.add_widget(Label(text="Día", size_hint_y=None, height=25))
        self.day_btn = Button(
            text=str(self.current_day),
            background_normal='', background_color=(1, 1, 1, 1), color=(0, 0, 0, 1),
            size_hint_y=None, height=45
        )
        self.day_btn.bind(on_press=self._open_day_popup)
        dia_col.add_widget(self.day_btn)

        fields_container.add_widget(ano_col)
        fields_container.add_widget(mes_col)
        fields_container.add_widget(dia_col)
        content.add_widget(fields_container)

        content.add_widget(Widget()) 

        btn_box = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=55)
        guardar_btn = Button(text="Guardar", background_color=(0, 0.6, 0, 1), bold=True)
        cancelar_btn = Button(text="Cancelar", background_color=(0.7, 0, 0, 1), bold=True)
        
        guardar_btn.bind(on_press=self._save_date)
        cancelar_btn.bind(on_press=self.dismiss)
        
        btn_box.add_widget(guardar_btn)
        btn_box.add_widget(cancelar_btn)
        content.add_widget(btn_box)

        self.content = content

    # --- utilidades para la nueva lógica dinámica ---
    def _is_restricted_target(self):
        # Acepta varias formas para evitar errores por nombres distintos en el resto del código
        restricted = ("salario", "regalo", "pecado", "gastos_fijos", "gastos fijos", "gasto_fijo", "gasto fijo")
        return str(self.target).lower() in restricted

    def _parse_year_input(self):
        txt = (self.year_input.text or "").strip()
        if txt == "":
            return None
        try:
            return int(txt)
        except:
            return None

    def _compute_month_day_states(self, year):
        """
        Devuelve un dict con estados para meses y (si se desea) para días.
        Estados para meses: "enabled", "disabled", "highlight"
        Si year es None se interpreta como presente (current year).
        """
        today = datetime.date.today()
        cur_y, cur_m, cur_d = today.year, today.month, today.day

        # Si year es None -> interpretamos como presente (current year)
        if year is None:
            year = cur_y

        states = {"months": {}, "days": {}}  # days se calcula en _open_day_popup según el mes

        if not self._is_restricted_target():
            # meta u otros: todo habilitado, sin highlights
            for m in range(1, 13):
                states["months"][m] = "enabled"
            return states

        # restricted targets: aplicar reglas
        if year < cur_y:
            for m in range(1, 13):
                states["months"][m] = "enabled"
            return states

        if year > cur_y:
            for m in range(1, 13):
                states["months"][m] = "disabled"
            return states

        # year == cur_y (presente)
        for m in range(1, 13):
            if m < cur_m:
                states["months"][m] = "enabled"
            elif m == cur_m:
                states["months"][m] = "highlight"
            else:
                states["months"][m] = "disabled"

        return states

    # --- reemplazo de _open_month_popup con lógica dinámica ---
    def _open_month_popup(self, instance):
        content = GridLayout(cols=3, spacing=10, padding=10)
        p = Popup(title='Seleccionar Mes', content=content, size_hint=(0.85, 0.6))

        year = self._parse_year_input()
        states = self._compute_month_day_states(year)

        for i, name in enumerate(self.month_names, 1):
            state = states.get("months", {}).get(i, "enabled")
            btn = Button(text=name, size_hint_y=None, height=50,
                         background_normal='', color=(0, 0, 0, 1))
            if state == "highlight":
                btn.background_color = (0.2, 0.5, 1, 1)  # azul destacado
                btn.disabled = False
            elif state == "disabled":
                btn.background_color = (0.9, 0.9, 0.9, 1)  # gris claro
                btn.disabled = True
            else:
                btn.background_color = (1, 1, 1, 1)
                btn.disabled = False

            # bind solo si no está disabled
            if not btn.disabled:
                btn.bind(on_press=lambda x, m=i, pop=p: self._select_month(m, x, pop))
            content.add_widget(btn)
        p.open()

    # --- reemplazo de _open_day_popup con lógica dinámica ---
    def _open_day_popup(self, instance):
        content = GridLayout(cols=7, spacing=5, padding=10)
        p = Popup(title='Seleccionar Día', content=content, size_hint=(0.9, 0.6))

        # parsear año; si está vacío -> None (presente)
        year = self._parse_year_input()

        # calcular días del mes usando year real si se proporcionó, o el año actual si no
        days = self._days_in_month(self.current_month, year if year is not None else datetime.date.today().year)

        today = datetime.date.today()
        cur_y, cur_m, cur_d = today.year, today.month, today.day

        for d in range(1, days + 1):
            btn = Button(text=str(d), size_hint_y=None, height=45,
                         background_normal='', color=(0, 0, 0, 1))
            disabled = False
            highlighted = False

            if not self._is_restricted_target():
                disabled = False
            else:
                # reglas cuando año > actual -> todo bloqueado
                if year is not None and year > cur_y:
                    disabled = True
                elif year is None or year == cur_y:
                    # si mes > cur_m -> bloquear todos
                    if self.current_month > cur_m:
                        disabled = True
                    elif self.current_month == cur_m:
                        if d > cur_d:
                            disabled = True
                        elif d == cur_d:
                            highlighted = True
                    else:
                        disabled = False
                else:
                    # year < cur_y -> todo habilitado
                    disabled = False

            if highlighted:
                btn.background_color = (0.2, 0.5, 1, 1)
                btn.disabled = False
            elif disabled:
                btn.background_color = (0.9, 0.9, 0.9, 1)
                btn.disabled = True
            else:
                btn.background_color = (1, 1, 1, 1)
                btn.disabled = False

            if not btn.disabled:
                btn.bind(on_press=lambda x, day=d, pop=p: self._select_day(day, x, pop))
            content.add_widget(btn)
        p.open()

    def _select_month(self, m, btn, popup):
        self.current_month = m
        self.month_btn.text = self.month_names[m-1]
        popup.dismiss()

    def _select_day(self, d, btn, popup):
        self.current_day = d
        self.day_btn.text = str(d)
        popup.dismiss()

    def _days_in_month(self, month, year):
        if month in [4, 6, 9, 11]: return 30
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0): return 29
            return 28
        return 31

    def _save_date(self, instance):
        try:
            y = int(self.year_input.text)
        except:
            y = self.current_year
        date_str = f"{y:04d}-{self.current_month:02d}-{self.current_day:02d}"
        if self.on_save:
            self.on_save(date_str)
        self.dismiss()