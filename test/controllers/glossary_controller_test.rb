#encoding: utf-8
require File.join(File.expand_path(File.dirname(__FILE__)), '..', 'test_helper')

class GlossaryControllerTest < ActionController::TestCase

  def setup
    super
    @controller = Api::V1::GlossaryController.new
    sleep 1
  end



  test "should add single Portuguese word term to dictionary" do
    authenticate_with_token
    post :term, data: '{"term": "teste", "lang": "pt", "definition": "teste definition","translations": [ {"lang": "pt","definition": "definição de teste","term": "teste"}],"context": {"tags":["T1","T2"], "source": {"url": "testSite.url","name": "test site"},"page_id":"test", "post": "xxxx","data_source": "dictionary","time-zone": "PDT / MST"}}'
    assert_response 200
  end


  test "should add single EN word term to dictionary" do
    authenticate_with_token
    post :term, data: '{"lang": "en", "definition": "test definition","term": "test3","translations": [ {"lang": "pt","definition": "definição de teste","term": "teste"}],"context": { "source": {"url": "testSite.url","name": "test site"},"tags":["tag1","tag2"],"post": "xxxx","data_source": "dictionary","time-zone": "PDT / MST"} }'
    assert_response 200
  end

  test "should add single Arabic word term to dictionary" do
    authenticate_with_token
    post :term, data: '{"lang": "ar", "definition": "test definition","term": "حكمة","translations": [ {"lang": "en","definition": "definição de teste","term": "teste"}],"context": { "source": {"url": "testSite.url","name": "test site"},"post": "xxxx", "page_id": "xxxx", "data_source": "dictionary","time-zone": "PDT / MST"} }'
    assert_response 200
  end

  test "should get single word EN term from dictionary" do
    authenticate_with_token
    get :terms, data: '{"lang": "en", "term": "test3" , "context":{"source":{"url":"testSite.url", "name":"test site"}}}'
    assert_response 200
  end

  test "should get single word term to dictionary from Arabic sentence" do
    authenticate_with_token
    get :terms, data: '{"lang": "ar", "post": "حكمة عظيمة","context": {"post": "xxxx"}}'
    assert_response 200
  end

  test "should get single word term to dictionary from Portuguese sentence" do
    authenticate_with_token
    get :terms, data: '{"lang": "pt", "term": "teste e outra palavra", "context": { "source": {"url": "testSite.url","name": "test site"}}}'
    assert_response 200
  end

  test "should get single word term to dictionary from Arabic sentence without language field" do
    authenticate_with_token
    get :terms, data: '{"post": "حكمة عظيمة"}'
    assert_response 200
  end

  test "should delete single word EN term from dictionary" do
    authenticate_with_token
    json = '{"lang": "en", "definition": "test definition","term": "test3","translations": [ {"lang": "pt","definition": "definição de teste","term": "teste"}],"context": { "source": {"url": "testSite.url","name": "test site"},"tags":["tag1","tag2"],"post": "xxxx","data_source": "dictionary","time-zone": "PDT / MST"} }'
    Mlg::ElasticSearch.add_glossary json
    get :terms, data: '{"lang": "en", "term": "test3", "context":{"source":{"url":"testSite.url", "name":"test site"}}}'
    data_hash = assigns(:glossary)[0]
    delete :delete, id: data_hash["_id"]
    assert_response 200
  end

  test "should delete single Arabic word term from dictionary" do
    authenticate_with_token
    Mlg::ElasticSearch.add_glossary '{"lang": "ar", "definition": "test definition","term": "حكمة","translations": [ {"lang": "en","definition": "definição de teste","term": "teste"}],"context": { "source": {"url": "testSite.url","name": "test site"},"post": "xxxx", "page_id": "xxxx", "data_source": "dictionary","time-zone": "PDT / MST"} }'
    get :terms, data: '{"lang": "ar", "term":  "حكمة", "context":{"source":{"url":"testSite.url", "name":"test site"}}}'
    data_hash = assigns(:glossary)[0]
    delete :delete, id: data_hash["_id"]
    assert_response 200
  end


  test "should delete single Portuguese word term from dictionary" do
    authenticate_with_token
    Mlg::ElasticSearch.add_glossary '{"term": "teste", "lang": "pt", "definition": "teste definition","translations": [ {"lang": "pt","definition": "definição de teste","term": "teste"}],"context": {"tags":["T1","T2"], "source": {"url": "testSite.url","name": "test site"},"page_id":"test", "post": "xxxx","data_source": "dictionary","time-zone": "PDT / MST"}}'
    sleep 1
    get :terms, data: '{"lang": "pt", "term":  "teste", "context":{"tags":["T1","T2"], "source":{"url":"testSite.url", "name":"test site"}}}'
    data_hash = assigns(:glossary)[0]
    delete :delete, id: data_hash["_id"]
    assert_response 200
  end

  test "should not create term if term is missing" do
    authenticate_with_token
    post :term, data: '{"lang": "pt", "definition": "test definition","translations": [ {"lang": "en","definition": "definição de teste","term": "teste"}],"context": { "source": {"url": "testSite.url","name": "test site"},"post": "xxxx","data_source": "dictionary","time-zone": "PDT / MST"} }'
    assert_response 400
  end

  test "should not create term if lang is missing" do
    authenticate_with_token
    post :term, data: '{ "term":"teste", "definition": "test definition","translations": [ {"lang": "en","definition": "definição de teste","term": "teste"}],"context": { "source": {"url": "testSite.url","name": "test site"},"post": "xxxx","data_source": "dictionary","time-zone": "PDT / MST"} }'
    assert_response 400
  end

  test "should not create duplicated term" do
    authenticate_with_token
    post :term, data: '{"lang": "pt", "term":"teste", "definition": "test definition","translations": [ {"lang": "en","definition": "definição de teste","term": "teste"}],"context": { "source": {"url": "testSite.url","name": "test site"},"post": "xxxx","data_source": "dictionary","time-zone": "PDT / MST"} }'
    sleep 1
    post :term, data: '{"lang": "pt", "term":"teste", "definition": "test definition","translations": [ {"lang": "en","definition": "definição de teste","term": "teste"}],"context": { "source": {"url": "testSite.url","name": "test site"},"post": "xxxx","data_source": "dictionary","time-zone": "PDT / MST"} }'
    assert_response 400
    sleep 1

    get :terms, data: '{"lang": "pt", "term":  "teste"}'
    data_hash = assigns(:glossary)[0]
    delete :delete, id: data_hash["_id"]

  end

  test "term - should return error if data was not provided" do
    authenticate_with_token
    post :term
    assert_response 400
  end

  test "term - should return error if data is empty" do
    authenticate_with_token
    post :term, data:''
    assert_response 400
  end

  test "term - should return error if invalid json" do
    authenticate_with_token
    post :term, data:'{lang:en, term:empty}'
    assert_response 400
  end

  test "terms - should return error if data was not provided" do
    authenticate_with_token
    get :terms
    assert_response 400
  end

  test "terms - should return error if data is empty" do
    authenticate_with_token
    get :terms, data:''
    assert_response 400
  end

  test "terms - should return error if invalid json" do
    authenticate_with_token
    assert_raises JSON::ParserError do
      get :terms, data:'{lang:en, term:empty}'
    end
  end

  test "delete - should return error if invalid id" do
    authenticate_with_token
    delete :delete, id:'00000000'
    assert_response 400
  end

  test "delete - should return error if data is empty" do
    authenticate_with_token
    delete :delete, data:''
    assert_response 400
  end

  test "delete - should return error if data was not provided" do
    authenticate_with_token
    delete :delete
    assert_response 400
  end

  test "should add, get and delete term (sequence)" do
    authenticate_with_token

    # The term
    term = {
      term: 'Test',
      lang: 'en', 
      definition: 'An experiment',
      translations: [
        { lang: 'pt', definition: 'Um experimento', term: 'Teste' },
        { lang: 'es', definition: 'Un experimento', term: 'Teste' }
      ],
      context: { page_id: 'foo', 'data_source' => 'glossary' }
    }.to_json

    # Add
    post :term, data: term
    assert_response :success

    # Get
    get :terms, data: { lang: 'en', term: 'This is just a test', context: { page_id: 'foo' } }.to_json
    assert_equal ['Test'], JSON.parse(@response.body)['data'].collect{ |t| t['_source']['term'].strip }.sort
    id = JSON.parse(@response.body)['data'][0]['_id']
    
    # Delete
    delete :delete, id: id
    assert_response :success

    # Get
    get :terms, data: { lang: 'en', term: 'This is just a test', context: { page_id: 'foo' } }.to_json
    assert_equal [], JSON.parse(@response.body)['data']
  end
end


