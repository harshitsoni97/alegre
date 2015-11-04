#encoding: utf-8
require File.join(File.expand_path(File.dirname(__FILE__)), '..', 'test_helper')

class LanguagesControllerTest < ActionController::TestCase
  def setup
    super
    @controller = Api::V1::LanguagesController.new
  end

  test "identification - should get language en" do
    authenticate_with_token
    get :identification, text: 'This is a sentence in English'
    assert_response :success
    assert_equal "en", assigns(:language)[0][1]   
  end

  test "identification - should get language es" do
    authenticate_with_token
    get :identification, text: 'Esta es una frase en español'
    assert_response :success
    assert_equal "es", assigns(:language)[0][1]   
  end

  test "identification - should get language pt" do
    authenticate_with_token
    get :identification, text: 'Esta é uma frase em português'
    assert_response :success
    assert_equal "pt", assigns(:language)[0][1]   
  end

  test "identification - should get language ar" do
    authenticate_with_token
    get :identification, text: 'هذه هي العبارة باللغة العربية'
    assert_response :success
    assert_equal "ar", assigns(:language)[0][1]   
  end


  test "identification - should return error empty if test is in a unknown language" do
    authenticate_with_token
    get :identification, text: 'sdflk skljfkdsf skdfjd jjas'
    assert_response :success
    assert_equal [], assigns(:language)
  end

  test "identification - should return error empty if test is in a unknown language - signs" do
    authenticate_with_token
    get :identification, text: '♥ →'
    assert_response :success
    assert_equal [], assigns(:language)
  end

  test "identification - should return english" do
    authenticate_with_token
    get :identification, text: 'I ♥ you English language'
    assert_response :success
    assert_equal "en", assigns(:language)[0][1]   
  end

  test "identification - should return english hashtah" do
    authenticate_with_token
    get :identification, text: '#English'
    assert_response :success
    assert_equal "en", assigns(:language)[0][1]   
  end


  test "identification - should return error if text blank" do
    authenticate_with_token
    get :identification, text: ''
    assert_response 400
  end


  test "identification - should return error if text was not provided" do
    authenticate_with_token
    get :identification
    assert_response 400
  end

  test "sample - should return error if no parameter was not provided" do
    authenticate_with_token
    get :sample
    assert_response 400
  end

  test "sample - should return error if language was not provided" do
    authenticate_with_token
    get :sample, text: '#English'
    assert_response 400
  end

  test "sample - should return error if text was not provided" do
    authenticate_with_token
    get :sample, language: 'en'
    assert_response 400
  end

  test "sample - should return sucess" do
    authenticate_with_token
    get :identification, text: 'sample text in english language'
    assert_response :success
  end

  test "sample - should return error if text blank" do
    authenticate_with_token
    get :sample, language: 'en', text: ''
    assert_response 400
  end

  test "sample - should return error if language blank" do
    authenticate_with_token
    get :sample, language: '', text: 'one example'
    assert_response 400
  end

  test "sample - should return error parameters blank" do
    authenticate_with_token
    get :sample, language: '', text: ''
    assert_response 400
  end


  test "language - should return list" do
    arrayVar = [1]
    authenticate_with_token
    get :language
    assert_response :success
    assert_equal arrayVar.class, assigns(:list).class
  end

end

