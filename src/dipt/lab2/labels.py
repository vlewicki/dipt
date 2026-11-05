from enum import StrEnum

class PIILabel(StrEnum):
    """Метки атрибутов ПДн, поддерживаемые пакетом."""
    SURNAME = "SURNAME"
    NAME = "NAME"
    EMAIL = "EMAIL"
    INN = "INN"
    PHONE = "PHONE"
    BANK_CARD = "BANK_CARDuse gpui::*;
    
    struct Counter {
        count: i32,
    }
    
    impl Render for Counter {
        fn render(&mut self, _: &mut Window, cx: &mut Context<Self>) -> impl IntoElement {
            div()
                .v_flex()
                .gap_2()
                .items_center()
                .child(format!("Count: {}", self.count))
                .child(
                    div()
                        .child("Increment")
                        .on_click(cx.listener(|this, _, _, cx| {
                            this.count += 1;
                            cx.notify(); // Request a re-render
                        })),
                )
        }
    }
    
    fn main() {
        gpui_platform::application().run(|cx: &mut App| {
            cx.open_window(WindowOptions::default(), |_, cx| {
                cx.new(|_| Counter { count: 0 })
            }).unwrap();
        });
    }"