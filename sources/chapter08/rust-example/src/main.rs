use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};
use askama::Template;
use dotenv::from_filename;
use sqlx::MySqlPool;
use std::env;

#[derive(Template)]
#[template(path = "index.html")]
struct IndexTemplate {
    value: i64,
}

#[derive(Template)]
#[template(path = "view.html")]
struct ViewTemplate {
    value: i64,
}

#[get("/")]
async fn index(db: web::Data<MySqlPool>) -> impl Responder {
    let rec = sqlx::query!("SELECT value FROM counter WHERE name = 'web' LIMIT 1")
        .fetch_optional(db.get_ref())
        .await
        .unwrap();

    let value = rec.and_then(|r| r.value.map(|v| v as i64)).unwrap_or(0i64);

    let template = IndexTemplate { value };
    HttpResponse::Ok()
        .content_type("text/html")
        .body(template.render().unwrap())
}

#[post("/increment")]
async fn increment(db: web::Data<MySqlPool>) -> impl Responder {
    let _ = sqlx::query!(
        r#"
        INSERT INTO counter (name, value) VALUES ('web', 1)
        ON DUPLICATE KEY UPDATE value = value + 1
        "#
    )
    .execute(db.get_ref())
    .await;

    HttpResponse::SeeOther()
        .insert_header(("Location", "/"))
        .finish()
}

#[get("/view")]
async fn view_counter(db: web::Data<MySqlPool>) -> impl Responder {
    let rec = sqlx::query!("SELECT value FROM counter WHERE name = 'web' LIMIT 1")
        .fetch_optional(db.get_ref())
        .await
        .unwrap();

    let value = rec.and_then(|r| r.value.map(|v| v as i64)).unwrap_or(0i64);

    let template = ViewTemplate { value };
    HttpResponse::Ok()
        .content_type("text/html")
        .body(template.render().unwrap())
}

/**
 * Running two instances of this server on different ports
 * cargo run -- mysql://root:root@127.0.0.1:3307/app_db 8080 #server 1
 * cargo run -- mysql://root:root@127.0.0.1:3308/app_db 8081 #server 2
 */

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let mut args = env::args().skip(1);
    let db_url = args.next().expect("Please provide a database URL");
    let port = args
        .next()
        .expect("Please provide a port number")
        .parse::<u16>()
        .expect("Invalid port number");

    let db = MySqlPool::connect(&db_url)
        .await
        .expect("Failed to connect to DB");

    println!("Running on port {}", port);

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(db.clone()))
            .service(index)
            .service(increment)
            .service(view_counter)
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
