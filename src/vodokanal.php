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

$all_elements;

$dateNow = date("d.m.Y");
echo "Date now: " . $dateNow . "\n";

foreach ($html->find('td[bgcolor="#ffffff"]') as $e) {
  $date = "";
  preg_match("/\\d{2}\\.\\d{2}\\.\\d{4}/", $e->plaintext, $date);

  if (strcasecmp(reset($date), $dateNow) == 0) { // get current date posts
    // remove date from content
    $content = str_replace(reset($date), "", $e->plaintext);
    $content = str_replace("\r\n \r\n", "", $content);
    $content = str_replace("\n\n", "", $content);
    // add post to array
    $all_elements[] = $content;
  }
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
    echo "No changes.";
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

function send_telegram_message($message)
{
  $message = str_replace(" ", "%20", $message); // fix for telegram
  global $config;
  $obj = json_decode(file_get_contents("https://api.telegram.org/bot" . $config['Telegram_token'] . "/sendMessage?chat_id=" . $config['Telegram_channel'] . "&disable_notification=" . $config['Send_silent'] . "&text=" . $message));

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
