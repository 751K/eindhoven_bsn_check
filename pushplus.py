import requests
import json

def send_pushplus_msg(token, title, content, template="html"):
    """
    发送PushPlus推送消息
    
    Args:
        token (str): PushPlus的token
        title (str): 消息标题
        content (str): 消息内容
        template (str): 消息模板，默认为html
    
    Returns:
        bool: 发送成功返回True，失败返回False
    """
    url = "http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": template
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 200:
            print(f"推送消息发送成功: {title}")
            return True
        else:
            print(f"推送消息发送失败: {result.get('msg', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"推送消息发送异常: {e}")
        return False 