# SoftTennisAceReview

## アプリケーション概要

ソフトテニスラケットのレビューを他の競技者と共有できる Web アプリケーションです。

### 目指した課題解決

#### 「ラケット選びの判断材料を増やす」という競技者のニーズに応えるとともに、「ソフトテニス業界の繁栄」を目指しました。

私は現在、社会人のソフトテニスクラブに所属しており、初級者の方や中学生、高校生と練習をする機会があります。  
そこで自分のレベルに合ったラケット選びをしていない方がいらっしゃいました。理由を伺ったところ、  
強い選手が使用していることや、デザイン性、Youtuber の方のレビューが主な決め手であるということが分かりました。  
そういった背景から、ラケット使用者の生の声をシェアできるものがあれば、初級者の方が自分に合ったラケットを見つけやすくなると考え、作成に至りました。

### URL

https://www.softtennis-ace-review.com

### テスト用アカウント

- メールアドレス/t1@t1.com
- パスワード/test1pass

## 主な機能

### ・ホーム画面(ログイン前、ログイン後)

<div style="display: flex; flex-wrap: wrap;">
  <img style="width: 45%; margin: 1%;" alt="ホーム画面(ログイン前)" 
    src="https://github.com/Sho-Kawa0501/SoftTennisAceReview/assets/120151638/341f12cb-6187-4e3c-8873-5addc16968f0">
  <img style="width: 45%; margin: 1%;"alt="ホーム画面(ログイン後)" 
    src="https://github.com/Sho-Kawa0501/SoftTennisAceReview/assets/120151638/9f382198-d53d-488e-8650-5865b0cb9725">  
</div>

### ・レビュー投稿機能(レビュー未投稿時の画面)

<div style="display: flex; flex-wrap: wrap;">
 <img style="width: 47%; margin: 1%;" alt="レビューリスト(ログイン前)" 
  src="https://github.com/Sho-Kawa0501/SoftTennisAceReview/assets/120151638/e98f77c2-ccee-441e-b89b-8486ae6a86cf">
 <img style="width: 47%; margin: 1%;" alt="レビューフォーム" 
  src="https://github.com/Sho-Kawa0501/SoftTennisAceReview/assets/120151638/75ecbe09-f46c-4224-9a82-ae182eb739c3">
</div>

### ・レビュー投稿機能(レビュー投稿済みの画面)

<div style="display: flex; flex-wrap: wrap;">
 <img style="width: 45%; margin: 1%;" alt="レビューリスト(ログイン後)" 
  src="https://github.com/Sho-Kawa0501/SoftTennisAceReview/assets/120151638/7b20fcac-c0aa-48cf-a98d-94476434c68b">
</div>

### ・マイページ(それぞれのページに遷移可能)

<div style="display: flex; flex-wrap: wrap;">
 <img style="width: 45%; margin: 1%;" alt="マイページ" 
  src="https://github.com/Sho-Kawa0501/SoftTennisAceReview/assets/120151638/27e57e8f-3951-40db-a205-107e145f44ee">
</div>

## 使用技術

| Category       | Technology Stack                           |
| -------------- | ------------------------------------------ |
| Frontend       | TypeScript, Next.js, redux-tool-kit        |
| Backend        | Python(3.11),Django-rest-framework(3.14.0) |
| Infrastructure | Render, Vercel                             |
| Database       | PostgreSQL(14.10)                          |
| Design         | tailwind-css                               |
| etc.           | GitHub, AmazonS3                           |

## 主な実装機能一覧

### 基本機能

- ログイン
- 新規会員登録
- ラケットの一覧表示
- ラケットの絞り込み機能(シリーズ)
- レビューの一覧表示

### ログイン後機能

- レビューの投稿・編集・削除
- レビューのお気に入り登録
- マイページ参照
  - プロフィール編集（ユーザー名、アイコン）
  - 投稿済みレビューの一覧表示
  - お気に入り登録済みレビューの一覧表示
- アカウント削除

## 今後実装したいもの

- プロフィールに「競技歴、年齢、性別、プレースタイル、使用中のラケット」などの項目を追加し、
  その条件に沿ってユーザーを検索できる機能
- お気に入り登録されている数を使用してレビューのランキングを表示させる機能
- それぞれのユーザーごとにおすすめのレビュー、ラケットを表示させる機能

## ER 図

![SoftTennisAceReviewER図](https://github.com/Sho-Kawa0501/SoftTennisAceReview/assets/120151638/f0cafb8e-45a0-4792-8fe4-f830d8a0a846)
