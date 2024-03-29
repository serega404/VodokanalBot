<?php

// Connect library
include('libs/simplehtmldom/simple_html_dom.php');

// Load config
$config = include('config.php');

$db = null;
if (file_exists("db.json")) {
  $db = json_decode(file_get_contents('./db.json', true), true);
  echo print_r($db);
} else {
  echo ("Database not exist\n");
}

// get DOM from URL
$html = file_get_html($config['url']);

$all_elements = null;

$dateNow = date("d.m.Y");
echo "Date now: " . $dateNow . "\n";

foreach ($html->find('td[bgcolor="#ffffff"]') as $e) {
  $date = "";
  preg_match("/(0[1-9]|1[0-9]|2[0-9]|3[01])[.](0[1-9]|1[0-2])[.](20[0-9][0-9]|[0-9][0-9])/", $e->plaintext, $date);

  if (strcasecmp(reset($date), $dateNow) == 0) { // get current date posts
    // remove date from content
    $content = str_replace(reset($date), "", $e->plaintext);
    $content = htmlspecialchars_decode($content);
    $content = str_replace("\r\n \r\n", "", $content);
    $content = str_replace("\n\n", "", $content);
    display_message($content);
    // add post to array
    $all_elements[] = $content;
  }
}

if ($all_elements == null) {
  echo "Posts not found\n";
  exit;
} 

echo "The number of posts for this day: " . count($all_elements) . "\n";

if ($db != null) {
  $diff = array_diff($all_elements, $db);
  if ($diff != null) {
    foreach ($diff as $e) {
      echo "Message sended.\n";
      send_telegram_message($e);
    }
  } else {
    echo "No changes.\n";
    exit;
  }
} else {
  foreach ($all_elements as $e) {
    echo "Message sended.\n";
    send_telegram_message($e);
  }
}

// save posts to database
$json = json_encode($all_elements, JSON_UNESCAPED_UNICODE);
file_put_contents("db.json", $json);

function display_message($message)
{
    echo "---- START MESSAGE ----\n";
    echo $message . "\n";
    echo "---- END MESSAGE ----\n";
}

function send_telegram_message($message)
{
  $t_message = urlencode($message);  // Url fix
  global $config;
  $obj = json_decode(file_get_contents("https://api.telegram.org/bot" . $config['Telegram_token'] . "/sendMessage?chat_id=" . $config['Telegram_channel'] . "&disable_notification=" . $config['Send_silent'] . "&text=" . $t_message));

  if ($http_response_header[0] != null && $http_response_header[0] == "HTTP/1.1 200 OK") {
    try {
      echo "Successfully sented message, mess id: " . $obj->{'result'}->{'message_id'} . "\n";
    } catch (Exception $e) {
      echo "Telegram: Не удалось записать id в файл\n";
    }
  } else {
    echo "Telegram: Не удачный запрос: " . $http_response_header[0] . "\n";
  }
}
