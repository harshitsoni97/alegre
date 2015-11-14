## MLG API

A REST API to Meedan's linguistic functionality.

## Installation

* Copy `config/config.yml.example` to `config/config.yml` and adjust the options
* Copy `config/database.yml.example` to `config/database.yml` and adjust the options
* Copy `config/initializers/secret_token.rb.example` to `config/initializers/secret_token.rb` and adjust the options
* Copy `config/initializers/errbit.rb.example` to `config/initializers/errbit.rb` and adjust the options
* Run `bundle install` to install dependencies
* Run `bundle exec rake db:migrate` to create database schema
* Run `bundle exec rake lapis:api_keys:create` to create API key
* Run `bundle exec rake swagger:docs` to generate web-based documentation
* Run `cd doc && make` to generate full documentation
* Run `rails s` and access API at http://localhost:3000/api

## Features

### Language identification

* Identify the language of a given text
* List supported languages
* Add training sample to a model file